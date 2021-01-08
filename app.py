from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from datetime import datetime
import string
import random
import json


app = Flask(__name__)
app.secret_key = 'SECRET_KEY_FOR_SESSION'

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


def random_string():
    rand_char = string.ascii_letters + string.digits + string.punctuation
    rand_str = ''.join(random.choices(rand_char, k=3))
    return rand_str


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
            password = list(password)

            # Adding the random characters
            password = [chr(ord(password[i])+2) + random_string()
                        for i in range(len(password))]    # Using List comprehension
            encrypted_pass = ''.join(password)
            # for data insertion in db
            params = (website, username, encrypted_pass)
            query = """ INSERT INTO AccountDetails (site,username,password) VALUES (%s, %s, %s) """
            message = insert(query, dataset)  # calling our custom insert function
            return render_template('add_details.html', msg=message)
        else:
            return render_template('add_details.html', msg="")
    else:
        return redirect(url_for('login'))


@app.route('/decrypt_details', methods=['POST'])
def decrypt_details():
    value_of_sno = request.form['sno']
    encrypted_pass = list(value_of_sno)
    decrypted_pass = [chr(ord(encrypted_pass[i])-2)
                      for i in range(0, len(encrypted_pass), 4)]
    decrypted_pass = ''.join(decrypted_pass)
    return jsonify({'output': decrypted_pass})


@app.route('/get_details', methods=['GET', 'POST'])
def get_details():
    if('username' in session):
        query = """ SELECT * FROM AccountDetails """
        account_details = select(query, ())
        print(len(account_details))
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
            query = """ INSERT INTO user_details (email_id,password,plain_pass) VALUES (%s, %s, %s) """
            message = insert(query, (email, password_hash, password,))  # calling our custom insert function 
            return redirect(url_for('login'))
        elif(len(user_details)!=0):
            return render_template('register.html', message="Email Id already registered!!!")
        elif(password!=repassword):
            return render_template('register.html', message="Password didn't matched!!!")

    return render_template('register.html')


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
    
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)

