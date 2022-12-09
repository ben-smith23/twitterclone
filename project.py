'''
This is a "hello world" flask webpage.
During the last 2 weeks of class,
we will be modifying this file to demonstrate all of flask's capabilities.
This file will also serve as "starter code" for your Project 5 Twitter webpage.

NOTE:
the module flask is not built-in to python,
so you must run pip install in order to get it.
After doing do, this file should "just work".
'''

from flask import Flask, render_template, send_from_directory, request, make_response
from flask_babel import Babel, gettext, ngettext


app = Flask(__name__)
app.config.['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

def get_locale():
    return 'en'
    request.accept_languages.best({})

import sqlite3

import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
# there is no standard file extension; people use .db .sql .sql3 .database
args = parser.parse_args()

@app.route('/')     
def root():
    con = sqlite3.connect(args.db_file)
    messages =[]
    sql = 'select sender_id, message, created_at from messages order by created_at desc'
    cur_messages = con.cursor() 
    cur_messages.execute(sql)
    for row_messages in cur_messages.fetchall():
        sql = 'select username, age from users where id='+str(row_messages[0])+';'
        cur_users = con.cursor()
        cur_users.execute(sql)
        for row_users in cur_users.fetchall():
            pass

        messages.append({
            'message': row_messages[1],
            'created_at': row_messages[2],
            'username': row_users[0],
            'age': row_users[1]
        })

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)
    return render_template('root.html', messages=messages, logged_in = False)

def print_debug_info():
    # GET method
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))

    # POST method
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))

    # cookies
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))

def are_credentials_good(username, password):
    # FIXME:
    # look inside the databasse and check if the password is correct for the user
    if username == 'haxor' and password == '1337':
        return True
    else:
        return False

@app.route('/login', methods=['GET', 'POST'])     
def login():
    print_debug_info()
    # requests (plural) library for downloading;
    # now we need request singular 
    username = request.form.get('username')
    password = request.form.get('password')
    print('username=', username)
    print('password=', password)

    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they submitted a form; we're on the POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we get here, then we're logged in
            #return 'login successful'

            # create a cookie that contains the username/password info

            template = render_template(
                'login.html', 
                bad_credentials=False,
                logged_in=True)
            #return template
            response = make_response(template)
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response

@app.route('/logout')     
def logout():
    return render_template('logout.html')

@app.route('/create_user', methods=['GET', 'POST'])     
def create_user():
    try:
        con = sqlite3.connect(args.db_file)
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('password')

    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)
    return render_template('create_user.html')

@app.route('/create_message')     
def create_message():
    return render_template('create_message.html')

@app.route('/delete_message')     
def delete_message():
    return render_template('delete_message.html')

@app.route('/edit_message')     
def edit_message():
    return render_template('edit_message.html')

@app.route('/static/<path>')     
def static_directory(path):
    return send_from_directory('static', path)

app.run()