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
def sql_query(sql, *query_params):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor(buffered = True)
    cursor.execute(sql, *query_params)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def sql_execute(sql, *query_params):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor(buffered = True)
    cursor.execute(sql, *query_params)
    db.commit()
    cursor.close()
    db.close()

# User can view basic site statistics (demonstrates some aggregate queries)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not 'id' in session:
        return redirect(url_for('start'))
    # Queries
    tot_users = "select count(id) from user"
    tot_questions = "select count(id) from question"
    tot_comments = "select count(id) from letter"
    comp_answers = "select count(id) from letter where votes > 5"
    avg_questions = "select avg(n) from(select count(q.id) as n from user u left outer join question q on u.id=q.user_id group by u.id) as avg_questions"
    avg_comments = "select avg(n) from(select count(l.id) as n from user u left outer join letter l on u.id=l.user_id group by u.id) as avg_comments"
    # Save results in lists
    sql_tot_users = sql_query(tot_users, [])
    sql_tot_questions = sql_query(tot_questions, [])
    sql_tot_comments = sql_query(tot_comments, [])
    sql_comp_answers = sql_query(comp_answers, [])
    sql_avg_questions = sql_query(avg_questions, [])
    sql_avg_comments = sql_query(avg_comments, [])
    # Put statistics in dictionary to be displayed on webpage
    admin_stats = {"user":sql_tot_users[0][0],
                "question":sql_tot_questions[0][0],
                "comment":sql_tot_comments[0][0],
                "complete_comment":sql_comp_answers[0][0],
                "avg_question":sql_avg_questions[0][0],
                "avg_comment":sql_avg_comments[0][0]}
    return render_template('admin.html', totals = admin_stats)

# User can create an account
@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if "email" in request.form:
        if request.form['password'] == request.form['retype-password']:
            # Choose an email address, and check if it already exists in the database
            session['email'] = request.form["email"]
            sql = "select count(email) from user where email = %s"
            query_params = [(session['email'],)]
            count_email = sql_query(sql, *query_params)
            if count_email[0][0] > 0:
                # Handle error if user inputs email that already exists in database
                session.pop("email")
                return render_template('createaccount.html', template_error = "Could not create account: email is part of another account")
            # Choose username, and check if it already exists in the database
            session['username'] = request.form["username"]
            sql = "select count(username) from user where username = %s"
            query_params = [(session['username'],)]
            count_usernames = sql_query(sql, *query_params)
            if count_usernames[0][0] > 0:
                # Handle error if user inputs username that already exists in database
                session.pop("username")
                return render_template('createaccount.html', template_error = "Could not create account: username is part of another account")
            # Choose a password
            password = request.form["password"]
            sql = "insert into user(username, email, password) values(%s, %s, %s)"
            query_params = [(session['username'], session['email'], password)]
            sql_execute(sql, *query_params)
            sql = "select last_insert_id()"
            user_id = sql_query(sql, [])
            session['id'] = user_id[0][0]
            return redirect(url_for('main'))
        else:
            return render_template('createaccount.html', template_error = "Could not create account: password fields do not match")
    return render_template('createaccount.html', template_error = "")

# User can delete an account
@app.route('/deleteaccount', methods=['GET', 'POST'])
def delete_account():
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if "delete-btn" in request.form:
            sql = "select id from user where username = %s"
            query_params = [(session['username'],)]
            user_id = sql_query(sql, *query_params)
            sql = "delete from user where id = %s"
            query_params = [(user_id[0][0],)]
            sql_execute(sql, *query_params)
            return redirect(url_for('start'))
        if "returnhome" in request.form:
            return redirect(url_for('main'))
    return render_template('deleteaccount.html')

# User can logout from their account
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if not 'id' in session:
        return redirect(url_for('start'))
    if "returnhome" in request.form:
        if request.form["returnhome"] == "Yes":
            session.pop("username", None)
            session.pop("email", None)
            session.pop("id", None)
            return redirect(url_for('start'))
        if request.form["returnhome"] == "No":
            return redirect(url_for('main'))
    return render_template('logout.html')

# The main page
@app.route('/main', methods=['GET', 'POST'])
def main():
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "GET":
        sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                from user u
                inner join question q on u.id = q.user_id"""
        questions = sql_query(sql, [])
    if request.method == "POST":
        # User creates a new question and it posts
        if "text" in request.form:
            question = request.form['text']
            category = request.form['categories']
            sql = "select id from user where username = %s"
            query_params = [(session['username'],)]
            user_id = sql_query(sql, *query_params)
            sql = "insert into question(content, category, user_id) values(%s, %s, %s)"
            if "submit" in request.form:
                query_params = [(question, category, user_id[0][0])]
                sql_execute(sql, *query_params)
                sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                        from user u
                        inner join question q on u.id = q.user_id"""
                questions = sql_query(sql, [])

        # User sorts questions by date posted / timestamp
        elif request.form["sorting"] == "1":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    order by q.time_stamp"""
            questions = sql_query(sql, [])

        # User sorts questions alphabetically
        elif request.form["sorting"] == "2":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    order by q.content"""
            questions = sql_query(sql, [])

        # User sorts questions by author
        elif request.form["sorting"] == "3":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    order by u.username"""
            questions = sql_query(sql, [])

        # User sorts questions by categories
        elif request.form["sorting"] == "4":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    order by q.category"""
            questions = sql_query(sql, [])

        # User sorts questions by number of comments, descending order
        elif request.form["sorting"] == "5":
            sql = """select u.username, q.content, q.category, q.time_stamp, q.id
                    from user u
                    inner join question q on u.id = q.user_id
                    inner join letter l on q.id = l.question_id
                    group by u.username, q.content, q.category, q.time_stamp, q.id
                    order by count(l.alphabet_letter) desc"""
            questions = sql_query(sql, [])
    template_data = [];
    for row in questions:
        template_data.append({"author": row[0], "post": row[1], "category": row[2], "time": row[3], "number": row[4]})
    return render_template('main.html', posts=template_data)

# User is linked to a page containing the chosen question and its associated comments
@app.route('/post/<question>', methods=['GET', 'POST'])
def post(question):
    if not 'id' in session:
        return redirect(url_for('start'))
    if question == "admin":
        return redirect(url_for('admin'))
    if question == "profile":
        return redirect(url_for('profile'))
    if question == "logout":
        return redirect(url_for('logout'))
    sql = """select l.id, l.sub_letter_id, l.time_stamp, l.alphabet_letter, u.id, u.username, count(v.letter_id)
                 from question q inner join letter l on l.question_id = q.id
                 inner join user u on l.user_id = u.id
                 left join vote v on v.letter_id = l.id
                 where q.id = %s
                 group by l.id, l.sub_letter_id, l.time_stamp, l.alphabet_letter, u.id, u.username"""
    query_params = [(question,)]
    letter_data = sql_query(sql, *query_params)
    if request.method == 'POST':
        if request.form.keys()[1] == "None":
            sql = "insert into letter(alphabet_letter, user_id, question_id, sub_letter_id) values(%s, %s, %s, %s)"
            query_params = [(request.form['text'], session['id'], question, None)]
            sql_execute(sql, *query_params)
        else:
            sql = "insert into letter(alphabet_letter, user_id, question_id, sub_letter_id) values(%s, %s, %s, %s)"
            query_params = [(request.form['text'], session['id'], question, list(request.form.keys()[1]))]
            sql_execute(sql, *query_params)
        return redirect(url_for('post', question = question))
    letter_dicts = []
    template_data = []
    for row in letter_data:
        sql = "select v.user_id from vote v where v.letter_id = %s and v.user_id = %s"
        query_params = [(row[0], session['id'])]
        result = sql_query(sql, *query_params)
        if(len(result) > 0):
            user_vote = True
        else:
            user_vote = False
        letter_dicts.append({"Id": row[0], "parent": row[1], "created": row[2], "content": row[3], "creator": row[4], "fullname": row[5], "upvote_count": row[6], "user_has_upvoted": user_vote})
    if len(letter_dicts) > 0:
        for letter in letter_dicts:
            if letter["parent"] == None:
                template_data.append(find_next_letter(letter_dicts, [letter]))
    sql = """select q.content, u.username, q.category
     from question q inner join user u on q.user_id = u.id
     where q.id = %s"""
    query_params = [(question,)]
    question_data = sql_query(sql, *query_params)
    if len(question_data) == 1:
        return render_template('post.html', comments = template_data, post = question_data[0][0], author = question_data[0][1], category = question_data[0][2])
    else:
        return render_template('post.html', comments = template_data)

def find_next_letter(letter_data, prior_data):
    count = 0
    parent_id = prior_data[-1]["Id"]
    new_chains = []
    for letter in letter_data:
        if letter["parent"] == parent_id:
            count += 1
            new_chains = new_chains + find_next_letter(letter_data, prior_data + [letter])
    if count == 0:
        new_chains.append(prior_data)
    return new_chains

# User can view basic profile information and update their email, username or password, and delete their account
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not 'id' in session:
        return redirect(url_for('start'))
    return render_template('profile.html', profile = session)

# User is directed to the start page upon loading the website
@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == "POST":
        sql = "select username, email, id from user where user.email = %s and user.password = %s"
        query_params = [(request.form['email'], request.form['password'])]
        result = sql_query(sql, *query_params)
        if len(result) == 1:
            session['username'] = result[0][0]
            session['email'] = result[0][1]
            session['id'] = result[0][2]
            return redirect(url_for('main'))
        else:
            return render_template('start.html', template_error="Could not login: incorrect username or password")
    return render_template('start.html', template_error="")

# User can update their email
@app.route('/updateemail', methods=['GET', 'POST'])
def update_email():
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "GET":
        sql = "select email from user where email = %s"
        query_params = [(session['email'],)]
        sql_execute(sql, *query_params)
    if request.method == "POST":
        new_email = request.form['new-email']
        sql = "select count(email) from user where email = %s"
        query_params = [(new_email,)]
        count_email = sql_query(sql, *query_params)
        if count_email[0][0] > 0:
            # Handle error if user inputs email that already exists in database
            return render_template('updateemail.html', template_error = "Could not update email: email is already a part of another account", profile = session)
        sql = "update user set email = %s where email = %s"
        query_params = [(new_email, session['email'])]
        sql_execute(sql, *query_params)
        session['email'] = new_email
        return redirect(url_for('profile'))
    return render_template('updateemail.html', template_error = "", profile = session)

# User can update their password
@app.route('/updatepassword', methods=['GET', 'POST'])
def update_password():
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "POST":
        if request.form['new-password'] == request.form['retype-new-password']:
            sql = "select count(username) from user where email = %s and password = %s"
            query_params = [(session["email"], request.form['old-password'])]
            count = sql_query(sql, *query_params)
            if count[0][0] == 1:
                sql = "update user set password = %s where password = %s"
                query_params = [(request.form['new-password'], request.form['old-password'])]
                sql_execute(sql, *query_params)
                return redirect(url_for('profile'))
            else:
                return render_template('updatepassword.html', template_error = "Could not change password: Incorrect old password")
        else:
            return render_template('updatepassword.html', template_error = "Could not change password: New password fields do not match")
    return render_template('updatepassword.html', template_error = "")

# User can update their username
@app.route('/updateusername', methods=['GET', 'POST'])
def delete_username():
    if not 'id' in session:
        return redirect(url_for('start'))
    if request.method == "GET":
        sql = "select username from user where username = %s"
        query_params = [(session['username'],)]
        sql_execute(sql, *query_params)
    if request.method == "POST":
        new_username = request.form['new-username']
        sql = "select count(username) from user where username = %s"
        query_params = [(new_username,)]
        count_usernames = sql_query(sql, *query_params)
        if count_usernames[0][0] > 0:
            # Handle error if user inputs username that already exists in database
            return render_template("updateusername.html", template_error = "Could not update username: username is already in use", profile = session)
        sql = "update user set username = %s where username = %s"
        query_params = [(new_username, session['username'])]
        sql_execute(sql, *query_params)
        session['username'] = new_username
        return redirect(url_for('profile'))
    return render_template('updateusername.html', template_error = "", profile = session)

if __name__ == '__main__':
    app.run(**config['app'])
