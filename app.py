from flask import Flask,request,render_template
from markupsafe import escape
import os
import pymysql
import pymysql.cursors
from datetime import datetime

app = Flask(__name__)

connection = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                             user='b263072c1ab18d',
                             password='e4aaaba1',
                             db='heroku_594ae4223a52c95',
                             #charset='urf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with connection.cursor() as cursor:
    sql="SELECT * FROM all_players"
    cursor.execute(sql)
    result=cursor.fetchall()

connection.commit()

@app.route('/about')
def index():
    return render_template("test.html",
                           current_time=str(datetime.now()))

@app.route('/')
def about():
    return render_template('index.html',
                           all_players=result)

@app.route('/user/<username>')
def user(username):
    return "<h1>User %s</h1>"%escape(username)

@app.route('/user/<int:post_id>')
def post(post_id):
    return "<h1>User %d</h1>"%post_id

@app.route('/index')
def connect_test():
    with connection.cursor() as cursor:
        sql="SELECT * FROM test WHERE gender=%s"
        cursor.execute(sql,('male'))
        result=cursor.fetchone()
    return (f"<h1>Hello, {result['name']}!<h1>")

if __name__ == '__main__':
    app.run(debug=True)