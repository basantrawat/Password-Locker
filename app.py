from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from cryptography.fernet import Fernet
import json


app = Flask(__name__)
app.secret_key = 'SECRET_KEY_FOR_SESSION'
# In Production you should store above key in .env file

# MYSQL connectivity through flask-mysqldb package
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'pass_locker'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def select(query,params):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query,params)
        data = cur.fetchall()
        return data
    except Exception as e:
        return e


def insert(query, params):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query, params)
        mysql.connection.commit()
        return "Details successfully added"
    except Exception as e:
        return e

MASTER_SECRET_KEY = b'zEJjbP2ETor-wsnOQn-6-vpODlGECjZcfSgVzA_cjQY='
# In Production you should store above key in .env file

def encrypt_pass(salt, password):
    key = MASTER_SECRET_KEY + salt
    f = Fernet(key)
    plain_pass = bytes(password, 'utf-8')
    encrypted_pass = f.encrypt(plain_pass)
    return encrypted_pass

def decrypt_pass(salt, encrypted_password):
    key = MASTER_SECRET_KEY + bytes(salt, 'utf-8')
    f = Fernet(key)
    plain_pass = f.decrypt(bytes(encrypted_password,'utf-8'))
    return plain_pass.decode('utf-8')

@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/add_details', methods=['GET', 'POST'])
def add_details():
    if('username' in session):
        if(request.method == 'POST'):
            website = request.form['website']
            username = request.form['username']
            password = request.form['password']
            
            salt = Fernet.generate_key()
            encrypted_pass = encrypt_pass(salt, password)

            # for data insertion in db
            params = (website, username, encrypted_pass, salt, password,)
            # I have also added the plain password in db in development phase
            # but should remove it for Security reasons
            query = """ INSERT INTO ac_dtl_fernet (site,username,password, pass_key, plain_pass) VALUES (%s, %s, %s, %s, %s) """
            message = insert(query, params)
            return render_template('add_details.html', msg=message)
        else:
            return render_template('add_details.html', msg="")
    else:
        return redirect(url_for('login'))

@app.route('/decrypt_details', methods=['POST'])
def decrypt_details():
    encrypted_pass = request.form['pass']
    pass_key = request.form['key']
    decrypted_pass = decrypt_pass(pass_key, encrypted_pass)
    return jsonify({'output': decrypted_pass})

@app.route('/get_details', methods=['GET', 'POST'])
def get_details():
    if('username' in session):
        query = """ SELECT * FROM ac_dtl_fernet """
        account_details = select(query, ())
        return render_template('get_details.html', posts=account_details)
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        
        query = """ SELECT * FROM user_details WHERE email_id = %s """   
        user_details = select(query,(email,))
        if(len(user_details)==0 and password==repassword):
            password_hash = generate_password_hash(password)
            # I have also added the plain password in db in development phase
            # but should remove it for Security reasons
            query = """ INSERT INTO user_details (email_id,password,plain_pass) VALUES (%s, %s, %s) """
            message = insert(query, (email, password_hash, password,))  # calling our custom insert function 
            return redirect(url_for('login'))
        elif(len(user_details)!=0):
            return render_template('register.html', message="Email Id already registered!!!")
        elif(password!=repassword):
            return render_template('register.html', message="Password didn't matched!!!")
    if('username' not in session):
        return render_template('register.html')
    else:
        return render_template('add_details.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']

        query = """ SELECT * FROM user_details WHERE email_id = %s """   
        user_details = select(query,(email,))        
        if(user_details):
            password_hash = user_details[0]['password']
            if(check_password_hash(password_hash, password)):
                session['username'] = email
                return redirect(url_for('add_details'))
            else:
                return render_template('login.html', message="Incorrect username or password!")
        return render_template('login.html', message="Incorrect username or password!")  
    if('username' not in session):
        return render_template('login.html')
    else:
        return render_template('add_details.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)


