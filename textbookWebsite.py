#Controller
from jsonpickle import encode
from jsonpickle import decode
from flask import Flask
from flask import abort, redirect, url_for
from flask import request
from flask import render_template
from flask import session
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from logging import Formatter
from userdao import UserDao
from user import User
from bookdao import BookDao
from book import Book
from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
from flask import current_app as app

app = Flask(__name__)
error = None

#DEFAULT
@app.route('/')
def index():
    return redirect(url_for('homepage'))

#HOMEPAGE
@app.route('/homepage', methods=['POST', 'GET'])
def homepage():
    if session.get('user') is not None:
        username = decode(session['user']).userid
    else:
        username = None
    return render_template('homepage.html', username=username)

#FINDTEXTBOOKS
@app.route('/findtextbooks', methods=['POST', 'GET'])
def findtextbooks():
    if session.get('user') is not None:
        username = decode(session['user']).userid
    else:
        username = None

    dao = BookDao()
    books = dao.selectAll()
    app.logger.debug("books: %r", books)
    return render_template('findtextbooks.html', **locals())

#YOURTEXTBOOKS
@app.route('/yourtextbooks', methods=['POST', 'GET'])
def yourtextbooks():
    if session.get('user') is not None:
        username = decode(session['user']).userid
    else:
        username = None
        return redirect(url_for('login'))

    dao = BookDao()
    books = dao.selectByUserid(username)
    app.logger.debug("books: %r", books)
    return render_template('yourtextbooks.html', **locals())

#DELETE TEXTBOOK
@app.route('/deletetextbook', methods=['POST', 'GET'])
def deletetextbook():
    deleteSelected = request.form['deletedValue']
    dao = BookDao()
    books = dao.selectByUserid(decode(session['user']).userid)
    toDelete = books[int(deleteSelected)]
    dao.delete(toDelete)
    return yourtextbooks()


#UPLOAD
@app.route('/uploadtextbook', methods=['POST', 'GET'])
def uploadtextbook():
    if session.get('user') is not None:
        username = decode(session['user']).userid
        email = decode(session['user']).email
    else:
        username = None
        email = None
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        subject = request.form['subject']
        course = request.form['course']
        condition = request.form['condition']
        price = request.form['price']

        boolError = isValidUpload(title, author, subject, course, condition, price)
        if boolError[0]:
            app.logger.debug('valid upload info')
            book = Book(title, author, subject, course, condition, price, username, email)
            dao = BookDao()
            dao.insert(book)
            return findtextbooks()
        else:
            error = boolError[1]

    app.logger.debug('error %r', error)

    return render_template('uploadtextbook.html', **locals())

def isValidUpload(title, author, subject, course, condition, price):
    dao = UserDao()
    users = dao.selectAll()

    if title is None or title == '' or author is None or author == '' or subject is None or subject == '' or condition is None or condition == ''  or price is None or price == '':
        error = 'Field left empty'
        return [False, error]

    error = None
    return [True, error]

#LOGIN
@app.route('/login', methods=['POST', 'GET'])
def login():
    app.logger.debug('in login')
    error = None

    if request.method == 'GET':
        app.logger.debug('got a GET request')
    if request.method == 'POST':
        if 'userid' in request.form and isValidLogin(request.form['userid'],request.form['password']):
            app.logger.debug('login successful')
            return homepage()
        else:
            app.logger.debug('invalid userid/pass')
            error = 'Invalid username or password'
    app.logger.debug('error: %r', error)
    return render_template('login.html', error=error)

def isValidLogin(userid, password):
    app.logger.debug('in isValidNewUser of login')
    app.logger.debug('userid of isValidNewUser login: %r', userid)
    app.logger.debug('password of isValidNewUser login: %r', password)
    dao = UserDao()
    user = dao.selectByUserid(userid)
    if (user is not None) and (userid == user.userid) and (sha256_crypt.verify(password, user.password)):
        session['user']=encode(user) # use an encoder to convert user to a JSON object for session
        return True
    else:
        return False

#LOGOUT
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user', None)
    return login()

#NEW USER
@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
    error = None
    app.logger.debug('in new user')
    if request.method == 'POST':
        app.logger.debug('past first if')
        userid = request.form['userid']
        password = request.form['password']
        confirmPass = request.form['confirmPass']
        app.logger.debug('past form requests')
        email = request.form['email']
        app.logger.debug('past form requests')

        boolError = isValidNewUser(userid, password, confirmPass, email)
        if boolError[0]:
            app.logger.debug('valid info')
            user = User(request.form['userid'], request.form['password'], request.form['email'])
            dao = UserDao()
            dao.insert(user)
            return login()
        else:
            error = boolError[1]

    app.logger.debug('about to render newuser.html')
    app.logger.debug('error %r', error)
    return render_template('newuser.html', error=error)

def isValidNewUser(userid, password, confirmPass, email):
    app.logger.debug('in isValidNewUser of newuser')
    dao = UserDao()
    users = dao.selectAll()
    for user in users:
        app.logger.debug('checking user: %r', user.userid)
        if user.userid == userid:
            app.logger.debug("username already taken")
            error = 'Username already taken'
            app.logger.debug('error %r', error)
            return [False, error]
    if len(userid) < 3:
        error = 'Username must have at least 3 characters'
        return [False, error]
    elif len(password) < 6:
        error = 'Password must have at least 6 characters'
        return [False, error]
    elif password != confirmPass:
        error = 'Entered passwords must match'
        return [False, error]
    elif email == "" or email is None or '@' not in email:
        error = 'Please Enter Valid Email Address'
        return [False, error]

    error = None
    return [True, error]

#LINK TO LOCALHOST
if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    streamhandler = logging.StreamHandler(sys.stderr)
    streamhandler.setLevel(logging.DEBUG)
    streamhandler.setFormatter(Formatter("[%(filename)s:%(lineno)s - %(funcName)10s() ] %(message)s"))
    app.logger.addHandler(streamhandler)
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8080, threaded=True)