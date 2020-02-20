from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from datetime import datetime
import string
import random

app = Flask(__name__)

# MYSQL connectivity through flask-mysqldb package
mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'passLocker'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


def randomStringGen():
    rand_characters = string.ascii_letters + string.digits + \
        string.punctuation  # + escapeChars(string.punctuation)
    randomStr = ''.join(random.choices(rand_characters, k=3))
    return randomStr


def select(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    return (data)


def insert(query, dataSet):
    cur = mysql.connection.cursor()
    cur.execute(query, dataSet)
    mysql.connection.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/passLocker', methods=['GET', 'POST'])
def passLocker():
    if(request.method == 'POST'):
        site = request.form.get('site')
        username = request.form.get('username')
        password = request.form.get('password')
        password = list(password)
        for i in range(len(password)):
            password[i] = chr(ord(password[i])+2) + randomStringGen()

        encryptedStrPwd = ''.join(password)
        dataSet = (site, username, encryptedStrPwd)
        query = """INSERT INTO AccountDetails (site,username,password) VALUES (%s, %s, %s)"""
        insert(query, dataSet)
        return render_template('passLocker.html', msg="Added Successfully")

    else:
        return render_template('passLocker.html', msg="")


@app.route('/decryptPass', methods=['GET', 'POST'])
@app.route('/getPass', methods=['GET', 'POST'])
def fetchData():
    query = """SELECT * FROM AccountDetails"""
    posts = select(query)

    if(request.method == 'POST'):
        sno = request.form.get('sno')
        encryptedPwd = list(sno)
        y = len(encryptedPwd)
        decryptedPwd = []
        for i in range(0, y, 4):
            decryptedPwd.append(chr(ord(encryptedPwd[i])-2))

        strDecryptedPwd = ''.join(decryptedPwd)
        return render_template('getPass.html', posts=posts, decryptedPwd=strDecryptedPwd)

    else:
        return render_template('getPass.html', posts=posts)



if __name__ == "__main__":
    app.run(debug=True)
