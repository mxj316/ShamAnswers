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


# For this example you can select a handler function by
# uncommenting one of the @app.route decorators.

@app.route('/')
def basic_response():
    return redirect(url_for('start'))

@app.route('/start', methods=['GET', 'POST'])
def start()

@app.route('/login', methods=['GET', 'POST'])
def login()

@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount()

@app.route('/main', methods=['GET', 'POST', 'remove'])
def main()

@app.route('/profile', methods=['GET', 'POST'])
def profile()

@app.route('/updateaccount', methods=['GET', 'POST'])
def update_account()

@app.route('/deleteaccount', methods=['GET', 'POST', 'remove'])
def delete_account()

@app.route('/logout', methods=['GET', 'POST'])
def logout()



if __name__ == '__main__':
    app.run(**config['app'])
{}
