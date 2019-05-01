import configparser
from flask import Flask, render_template, redirect, url_for, request, flash, session
import mysql.connector
import datetime as datetime
import os

# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')
my_user = None  # will hold user id whene logged in
# Set up application server.
app = Flask(__name__)
app.config.update(**config['app'])
app.secret_key = os.urandom(24)

# Create a function for fetching data from the database.
def sql_query(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor(buffered = True)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def sql_execute(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor(buffered = True)
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')

# User can create an account
@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if "email" in request.form:
        # Choose an email address, and check if it already exists in the database
        session['email'] = request.form["email"]
        sql = "select count(email) from user where email = '{user_email}'".format(user_email = session['email'])
        count_email = sql_query(sql)
        if count_email[0][0] > 0:
            # Handle error if user inputs email that already exists in database
            session.pop("email")
            return render_template('createaccount.html', template_error = "Could not create account: email is part of another account")
        # Choose username, and check if it already exists in the database
        session['username'] = request.form["username"]
        sql = "select count(username) from user where username = '{username}'".format(username = session['username'])
        count_usernames = sql_query(sql)
        if count_usernames[0][0] > 0:
            # Handle error if user inputs username that already exists in database
            session.pop("username")
            return render_template('createaccount.html', template_error = "Could not create account: username is part of another account")
        # Choose a password
        password = request.form["password"]
        session['authorized'] = False
        sql = "insert into user(username, email, password) values('{username}', '{email}', '{password}')".format(username = session['username'], email = session['email'], password = password)
        sql_execute(sql)
        return redirect(url_for('main'))
    return render_template('createaccount.html', template_error = "")

# User can delete an account
@app.route('/deleteaccount', methods=['GET', 'POST'])
def delete_account():
    if request.method == "POST":
        if "Yes" in request.form:
            sql = "delete * from user where id = '{user_id}'".format(user_id = ___)
            sql_execute(sql)
            return redirect(url_for('start'))
        if "No" in request.form:
            return redirect(url_for('main'))
    return render_template('deleteaccount.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    print(request.form)
    if "returnhome" in request.form:
        if request.form["returnhome"] == "Yes":
            session.pop("username", None)
            session.pop("email", None)
            session.pop("authorized", None)
            return redirect(url_for('start'))
        if request.form["returnhome"] == "No":
            return redirect(url_for('main'))
    return render_template('logout.html')

@app.route('/posts', methods=['GET','POST'])
def posts():
    # Get all posts
    if request.method == "GET":
        sql = "select * from question"
        data = sql_execute(sql)
    return render_template('posts.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == "POST":
        # User creates a new question and it posts
        if "text" in request.form:
            question = request.form['text']
            category = request.form['categories']
            sql = "select id from user where username = '{username}'".format(username = session['username'])
            user_id = sql_query(sql)
            sql = "insert into question(content, category, user_id) values('{question}', '{category}', '{user_id}')".format(question = question, category = category, user_id = user_id)
            if "Post" in request.form:
                sql_execute(sql)
                template_data = {}
                sql = """select u.username, q.content, q.category, q.time_stamp
                        from user u
                        inner join question q on u.id = q.user_id
                        inner join letter l on q.id = l.question_id"""
                questions = sql_query(sql)
                # Render the data on the website

        # User sorts questions alphabetically
        elif request.form["sorting"] == "1" and "Sort" in request.form:
            sql = """select u.username, q.content, q.category, q.time_stamp
                    from user u
                    inner join question q on u.id = q.user_id
                    inner join letter l on q.id = l.question_id
                    order by q.content"""
            ord_abc = sql_query(sql)
            # Render the data on the website
            template_data = {}

        # User sorts questions by date posted / timestamp
        elif request.form["sorting"] == "2" and "Sort" in request.form:
            sql = """select u.username, q.content, q.category, q.time_stamp
                    from user u
                    inner join question q on u.id = q.user_id
                    inner join letter l on q.id = l.question_id
                    order by q.time_stamp"""
            ord_time_stamp = sql_query(sql)
            # Render the data on the website
            template_data = {}

        # User sorts questions by author
        elif request.form["sorting"] == "3" and "Sort" in request.form:
            sql = """select u.username, q.content, q.category, q.time_stamp
                    from user u
                    inner join question q on u.id = q.user_id
                    inner join letter l on q.id = l.question_id
                    order by u.username"""
            ord_author = sql_query(sql)
            # Render the data on the website
            template_data = {}

        # User sorts questions by categories
        elif request.form["sorting"] == "4" and "Sort" in request.form":
            sql = """select u.username, q.content, q.category, q.time_stamp
                    from user u
                    inner join question q on u.id = q.user_id
                    inner join letter l on q.id = l.question_id
                    order by q.category"""
            ord_cats = sql_query(sql)
            # Render the data on the website
            template_data = {}

        # User sorts questions by number of comments, descending order
        else:
            sql = """select u.username, q.content, q.category, q.time_stamp
                    from user u
                    inner join question q on u.id = q.user_id
                    inner join letter l on q.id = l.question_id
                    group by u.username, q.content, q.category, q.time_stamp
                    order by count(l.alphabet_letter) desc"""
            ord_num_comments = sql_query(sql)
            # Render the data on the website
            template_data = {}

    return render_template('main.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html', profile = session)

@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == "POST":
        sql = "select username, email from user where user.email='{email}' and user.password='{password}'".format(email = request.form['email'], password = request.form['password'])
        result = sql_query(sql)
        if len(result) == 1:
            session['username'] = result[0][0]
            session['email'] = result[0][1]
            return redirect(url_for('main'))
        else:
            return render_template('start.html', template_error="Could not login: incorrect username or password")
    return render_template('start.html', template_error="")

# User can update their email
@app.route('/updateemail', methods=['GET', 'POST'])
def update_email():
    if request.method == "GET":
        sql = "select email from user where email = '{email}'".format(email = session['email'])
        sql_execute(sql)
    if request.method == "POST":
        new_email = request.form['new-email']
        sql = "select count(email) from user where email = '{email}'".format(email = new_email)
        count_email = sql_query(sql)
        if count_email[0][0] > 0:
            # Handle error if user inputs email that already exists in database
            return render_template('updateemail.html', template_error = "Could not update email: email is already a part of another account", profile = session)
        sql = "update user set email = '{new_email}'".format(new_email = new_email)
        sql_execute(sql)
        session['email'] = new_email
        return redirect(url_for('profile'))
    return render_template('updateemail.html', template_error = "", profile = session)

# User can update their password
@app.route('/updatepassword', methods=['GET', 'POST'])
def update_password():
    if request.method == "POST":
        sql = "select count(username) from user where email = '{email}' and password='{password}'".format(email = session["email"], password = request.form['old-password'])
        count = sql_query(sql)
        print(count)
        if count[0][0] == 1:
            sql = "update user set password = '{new_password}'".format(new_password = request.form['new-password'])
            sql_execute(sql)
            return redirect(url_for('profile'))
        else:
            return render_template('updatepassword.html', template_error = "Could not change password: Incorrect old password")
    return render_template('updatepassword.html', template_error = "")

# User can update their username
@app.route('/updateusername', methods=['GET', 'POST'])
def delete_username():
    if request.method == "GET":
        sql = "select username from user where username = '{username}'".format(username = session['username'])
        sql_execute(sql)
    if request.method == "POST":
        new_username = request.form['new-username']
        sql = "select count(username) from user where username = '{username}'".format(username = new_username)
        count_usernames = sql_query(sql)
        if count_usernames[0][0] > 0:
            # Handle error if user inputs username that already exists in database
            return render_template("updateusername.html", template_error = "Could not update username: username is already in use", profile = session)
        sql = "update user set username = '{new_username}'".format(new_username = new_username)
        sql_execute(sql)
        session['username'] = new_username
        return redirect(url_for('profile'))
    return render_template('updateusername.html', template_error = "", profile = session)

if __name__ == '__main__':
    app.run(**config['app'])
