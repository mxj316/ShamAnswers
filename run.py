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
    sql = "select count(id) from user where username = '{username}' and admin is true".format(username = session['username'])
    admin_user = sql_query(sql)
    if admin_user[0][0] > 0:
    # if session['authorized'] == True:
        tot_users = "select count(id) from user"
        tot_questions = "select count(id) from question"
        tot_comments = "select count(id) from letter"
        comp_answers = "select count(id) from letter where votes > 5"
        avg_questions = "select avg(n) from(select count(q.id) as n from user u inner join question q on u.id=q.user_id group by u.id) as avg_questions"
        avg_comments = " select avg(n) from(select count(l.id) as n from user u inner join letter l on u.id=l.user_id group by u.id) as avg_comments"

        # Render these queries onto webpage

    else:
        return render_template('admin.html', template_error = "You are trying to access information that requires administrative privileges. Please contact an admin for more informatiion")
        return redirect(url_for('main'))
    return render_template('admin.html')

# User can create an account
@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if "email" in request.form:
        if request.form['password'] == request.form['retype-password']:
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
            # TODO: Decide how a user becomes an admin, and where in code this is to be done!
            session['authorized'] = False
            sql = "insert into user(username, email, password, admin) values('{username}', '{email}', '{password}', {admin})".format(username = session['username'], email = session['email'], password = password, admin = 0)
            sql_execute(sql)
            return redirect(url_for('main'))
        else:
            return render_template('createaccount.html', template_error = "Could not create account: password fields do not match")
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



@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == "POST":
        # User creates a new question and it posts
        if "text" in request.form:
            question = request.form['text']
            category = request.form['categories']
            sql = "select id from user where username = '{username}'".format(username = session['username'])
            user_id = sql_query(sql)
            sql = "insert into question(content, category, user_id) values('{question}', '{category}', '{user_id}')".format(question = question, category = category, user_id = user_id[0][0])
            if "submit" in request.form:
                sql_execute(sql)
                sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                        from user u
                        inner join question q on u.id = q.user_id"""
                questions = sql_query(sql)
                # Render the data on the website
        # User sorts questions alphabetically
        elif request.form["sorting"] == "1":
            sql = """select u.username, q.content,  q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    order by q.content"""
            questions = sql_query(sql)

        # User sorts questions by date posted / timestamp
        elif request.form["sorting"] == "2":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    order by q.time_stamp"""
            questions = sql_query(sql)

        # User sorts questions by author
        elif request.form["sorting"] == "3":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    order by u.username"""
            questions = sql_query(sql)

        # User sorts questions by categories
        elif request.form["sorting"] == "4":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    order by q.category"""
            questions = sql_query(sql)

        # User sorts questions by number of comments, descending order
        elif request.form["sorting"] == "5":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    inner join letter l on q.id = l.question_id
                    group by u.username, q.content, q.category, q.time_stamp
                    order by count(l.alphabet_letter) desc"""
            questions = sql_query(sql)
        template_data = [];
        for row in questions:
            template_data.append({"author": row[0], "post": row[1], "category": row[2], "number": row[4]}) 
        print(template_data)
        return render_template('main.html', posts=template_data)

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
        if request.form['new-password'] == request.form['retype-new-password']:
            sql = "select count(username) from user where email = '{email}' and password='{password}'".format(email = session["email"], password = request.form['old-password'])
            count = sql_query(sql)
            print(count)
            if count[0][0] == 1:
                sql = "update user set password = '{new_password}'".format(new_password = request.form['new-password'])
                sql_execute(sql)
                return redirect(url_for('profile'))
            else:
                return render_template('updatepassword.html', template_error = "Could not change password: Incorrect old password")
        else:
            return render_template('updatepassword.html', template_error = "Could not change password: New password fields do not match")
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
