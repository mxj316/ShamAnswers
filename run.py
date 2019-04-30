import configparser
from flask import Flask, render_template, redirect, url_for, request, flash, session
import mysql.connector
import datetime as datetime
from User import User
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
    return render_template('admin.html')

@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if "email" in request.form:
        session['email'] = request.form["email"]
        session['username'] = request.form["username"]
        session['authorized'] = False 
        return redirect(url_for('main'))
    return render_template('createaccount.html')

@app.route('/deleteaccount', methods=['GET', 'POST'])
def delete_account():
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
    if request.method == "GET":
        #Get all questions from db
        sql="select * from question"
        data= sql_execute(sql)
    return render_template('posts.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == "POST":
        # User creates a new question
        ques = request.form['text']
        # Define the user id
        sql = "insert into question(content, category, user_id) values(ques, {category}, {user_id})".format(category = ___, user_id = ___)
        sql_execute(sql)
    return render_template('main.html') 

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html', profile = session)

@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('start.html')

@app.route('/updateemail', methods=['GET', 'POST'])
def update_email():
    return render_template('updateemail.html')

@app.route('/updatepassword', methods=['GET', 'POST'])
def update_password():
    return render_template('updatepassword.html')

@app.route('/updateusername', methods=['GET', 'POST'])
def delete_username():
    return render_template('updateusername.html')

if __name__ == '__main__':
    app.run(**config['app'])
