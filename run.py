import configparser
from flask import Flask, render_template, redirect, url_for, request, flash, session
import mysql.connector
import datetime as datetime
from User import User

# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')
my_user = None  # will hold user id whene logged in
# Set up application server.
app = Flask(__name__)
app.secret_key = 'my_key_is_set_here'

# Create a function for fetching data from the database.
def sql_query(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def sql_execute(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html', template_data=template_data)

@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    return render_template('createaccount.html', template_data=template_data)

@app.route('/deleteaccount', methods=['GET', 'POST'])
def delete_account():
    return render_template('deleteaccount.html', template_data=template_data)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('logout.html', template_data=template_data)

@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == "post":
        # User creates a new question
        ques = request.form['text']
        # Define the user id
        sql = "insert into question(content, category, user_id) values(ques, {category}, {user_id})".format(category = ___, user_id = ___)
        sql_execute(sql)
    return render_template('main.html', template_data=template_data)

<<<<<<< HEAD
@app.route('/updateemail', methods=['GET', 'POST'])
def update_email()

@app.route('/updateusername', methods=['GET', 'POST'])
def update_username()

@app.route('/updatepassword', methods=['GET', 'POST'])
def update_password()
=======
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html', template_data=template_data)
>>>>>>> e373a81dea9abda7dcb07f1a515e2a8b37a30ce1

@app.route('/start', methods=['GET', 'POST'])
def start():
    return render_template('start.html', template_data=template_data)

@app.route('/updateemail', methods=['GET', 'POST'])
def update_email():
    return render_template('updateemail.html', template_data=template_data)

@app.route('/updatepassword', methods=['GET', 'POST'])
def update_password():
    return render_template('updatepassword.html', template_data=template_data)

@app.route('/updateusername', methods=['GET', 'POST'])
def delete_username():
    return render_template('updateusername.html', template_data=template_data)

if __name__ == '__main__':
    app.run(**config['app'])
