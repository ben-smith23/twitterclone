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
#app.config.['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

def get_locale():
    return 'en'
    request.accept_languages.best({})

import sqlite3, json
from datetime import datetime
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
        sql = 'select username, age from users where id=?;'
        cur_users = con.cursor()
        cur_users.execute(sql, [row_messages[0]])
        
        for row_users in cur_users.fetchall():
            pass

        messages.append({
            'message': row_messages[1],
            'created_at': row_messages[2],
            'username': row_users[0],
            'profpic': 'https://robohash.org/' + row_users[0],
            'age': row_users[1]
        })

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)
    return render_template('root.html', messages=messages, good_credentials=good_credentials, logged_in = False)

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

@app.route('/home.json')
def home_json():
    con = sqlite3.connect(args.db_file)
    cur = con.cursor()
    cur.execute('''
        SELECT sender_id, message, created_at, id from messages;''')
    rows = cur.fetchall()
    messages = []
    for row in rows:
        messages.append({'username': row[0], 'text': row[1], 'created_at':row[2], 'id':row[3]})
    messages.reverse()

    return json.dumps(messages)

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
    response = make_response(render_template('logout.html'))
    response.set_cookie('username', '', expires=0)
    response.set_cookie('password', '', expires=0)
    return response
    return render_template('logout.html')

@app.route('/create_user', methods=['GET', 'POST'])     
def create_user():
    try:
        if request.form.get('username'):
                if request.form.get('password1') == request.form.get('password2'):
                    con = sqlite3.connect(args.db_file)
                    cur = con.cursor()
                    cur.execute('''
                        INSERT INTO users (username, password, age) values (?,?,?);
                    ''', (request.form.get('username'), request.form.get('password1'), request.form.get('age')))
                    con.commit()
                    return make_response(render_template('create_user.html', successful = True))
                else: 
                    return make_response(render_template('create_user.html', successful = False, wrongPass=True))
        else: 
            return make_response(render_template('create_user.html'))
    except sqlite3.IntegrityError: 
        return render_template('create_user.html', taken=True, username=request.form.get('username'))

@app.route('/create_message')     
def create_message():
    username = request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    if request.cookies.get('username') :
        if request.form.get('newmessage'):
            con = sqlite3.connect(args.db_file)
            cur = con.cursor()
            sql = 'SELECT id from users where username=?;'
            cur.execute(sql, [username])
            for user in cur.fetchall():
                pass
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            # +0.5 EC - formatting date & time without decimals 
            cur.execute('''
                INSERT INTO messages (sender_id, message, created_at) values (?,?,?);
            ''', [user[0], request.form.get('newmessage'), dt_string])
            try:
                con.commit()
            except:
                print("didn\'t work")
            return make_response(render_template('create_message.html', created=True, good_credentials=good_credentials ))
        else: 
            return make_response(render_template('create_message.html', created=False, good_credentials=good_credentials))
    else:
        return login()

@app.route('/delete_account/<username>')
def delete_account(username):
    if request.cookies.get('username') == username: 
        con = sqlite3.connect(args.db_file)
        cur = con.cursor()
        sql = 'SELECT id from users where username=?;'
        cur.execute(sql, [username])
        for user in cur.fetchall():
            pass
        cur.execute('''
            DELETE from messages where id=?;
        ''', [user[0]])

        cur.execute('''
            DELETE from users where username=?;
        ''', [username])
        con.commit()
        response = make_response(render_template('delete_account.html'))
        response.set_cookie('username', '', expires=0)
        response.set_cookie('password', '', expires=0)

        return make_response(render_template('delete_account.html', not_your_username=False, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else: 
        return make_response(render_template('delete_account.html', not_your_username=True, username=request.cookies.get('username'), password=request.cookies.get('password')))

@app.route('/delete_message/<id>', methods=['GET'])
def delete_message(id):
    con = sqlite3.connect(args.db_file) 
    cur = con.cursor()
    cur.execute('''
        SELECT sender_id from messages where id=?;
    ''', (id,))
    rows = cur.fetchall()
    if rows[0][0] == request.cookies.get('username'):
        cur.execute('''
            DELETE from messages where id=?;
        ''', (id,))
        con.commit()
    else:
        return make_response(render_template('delete_message.html', not_your_message=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
    return make_response(render_template('delete_message.html', username=request.cookies.get('username'), password=request.cookies.get('password')))
# fix & make it work, add in table?

@app.route('/edit_message/<id>', methods=['POST', 'GET'])
def edit_message(id):
    if request.form.get('newmessage'):
        con = sqlite3.connect(args.db_file) 
        cur = con.cursor()
        cur.execute('''
            SELECT sender_id, message from messages where id=?;
        ''', (id,))
        rows = cur.fetchall()
        if rows[0][0] == request.cookies.get('username'):
            cur.execute('''
                UPDATE messages
                SET message = ?
                WHERE id = ?
            ''', (request.form.get('newmessage'),id))
            con.commit()
            return make_response(render_template('edit_message.html',allGood=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else:
            return make_response(render_template('edit_message.html',not_your=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return make_response(render_template('edit_message.html',default=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
# fix & make it work

@app.route('/search_message', methods=['POST', 'GET'])
def search_message():
    if request.form.get('search'):
        con = sqlite3.connect(args.db_file) 
        cur = con.cursor()
        cur.execute('''
            SELECT users.username, messages.message, messages.created_at, messages.id from messages join users ON messages.sender_id=users.id;
        ''')
        rows = cur.fetchall()
        messages = []
        for row in rows:
            if request.form.get('search') in row[1]:
                messages.append({'username': row[0], 'text': row[1], 'created_at':row[2], 'id':row[3]})
        messages.reverse()
        return render_template('search_message.html', messages=messages, username=request.cookies.get('username'), password=request.cookies.get('password'))
    else:
        return render_template('search_message.html', default=True, username=request.cookies.get('username'), password=request.cookies.get('password'))
    
@app.route('/change_password/<username>', methods=['post', 'get'])
def change_password(username):
    if request.form.get('oldPassword'):
        if request.cookies.get('username') == username:
            con = sqlite3.connect(args.db_file) 
            cur = con.cursor()
            cur.execute('''
                SELECT password from users where username=?;
            ''', (username,))
            rows = cur.fetchall()
            oldPassword = rows[0][0]
            
            if request.form.get('oldPassword') == oldPassword:
                if request.form.get('password1') == request.form.get('password2'):
                    cur.execute('''
                        UPDATE users
                        SET password = ?
                        WHERE username = ?
                    ''', (request.form.get('password1'), request.cookies.get('username')))
                    con.commit()
                    return make_response(render_template('change_password.html', allGood=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
                else: 
                    return make_response(render_template('change_password.html', repeatPass=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
            else: 
                return make_response(render_template('change_password.html', wrongPass=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else: 
            return make_response(render_template('change_password.html', not_your_username=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else: return make_response(render_template('change_password.html', username=request.cookies.get('username'), password=request.cookies.get('password')))


@app.route('/user')
def user():
    if(request.cookies.get('username') and request.cookies.get('password')):
        username = request.cookies.get('username')
        password=request.cookies.get('password')
        good_credentials = are_credentials_good(username, password)
        con = sqlite3.connect(args.db_file)
        cur = con.cursor()
        cur.execute('''
            SELECT message, created_at, id from messages where sender_id=?;
        ''', (request.cookies.get('username'),))
        rows = cur.fetchall()
        messages = []
        for row in rows:
            messages.append({'text': row[0], 'created_at': row[1], 'id':row[2]})
        messages.reverse()
        return make_response(render_template('user.html', messages=messages, username=request.cookies.get('username'), good_credentials=good_credentials))
    else: 
        return login()

@app.route('/static/<path>')
def static_directory(path):
    print_debug_info()
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run()
    # app.run(host="0.0.0.0")
