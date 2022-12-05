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

from flask import Flask, render_template, send_from_directory, request
app = Flask(__name__)

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
    return render_template('root.html', messages=messages, logged_in = False)

@app.route('/login')     
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    return render_template('login.html')

@app.route('/logout')     
def logout():
    return render_template('logout.html')

@app.route('/create_user')     
def create_user():
    return render_template('create_user.html')

@app.route('/create_message')     
def create_message():
    return render_template('create_message.html')

@app.route('/static/<path>')     
def static_directory(path):
    return send_from_directory('static', path)

app.run()