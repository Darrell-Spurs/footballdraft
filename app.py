from flask import Flask,request,render_template
from markupsafe import escape
import os
import pymysql
import pymysql.cursors

app = Flask(__name__)

connection = pymysql.connect(host=os.environ.get('CLEARDB_DATABASE_HOST'),
                             user=os.environ.get('CLEARDB_DATABASE_USER'),
                             password=os.environ.get('CLEARDB_DATABASE_PASSWORD'),
                             db=os.environ.get('CLEARDB_DATABASE_DB'),
                             charset='urf8mb4',
                             cursorclass=pymysql.cursors.DictCursor
)

with connection.cursor() as cursor:
    sql="INSERT INTO test(name) VALUES(%s,%s)"
    cursor.execute(sql,('Fishead','male'))

connection.commit()

@app.route('/')
@app.route('/index')
def index():
    return "<h1>Deployed update<h1>"

@app.route('/about')
def about():
    return render_template('test.html')

@app.route('/user/<username>')
def user(username):
    return "<h1>User %s</h1>"%escape(username)

@app.route('/user/<int:post_id>')
def post(post_id):
    return "<h1>User %d</h1>"%post_id

@app.route('/table')
def connect_test():
    with connection.cursor() as cursor:
        sql="SELECT * FROM test WHERE gender=%s"
        cursor.execute(sql,('male'))
        result=cursor.fetchone()
        print(result)
    return f"<h1>Hi, {result[0]['name']} and {result[1]['name']}!<h1>"

if __name__ == '__main__':
    app.run(debug=True)

