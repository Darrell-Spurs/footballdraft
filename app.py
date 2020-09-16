from flask import Flask,request,render_template, url_for
from markupsafe import escape
import os
import pymysql
import pymysql.cursors
import csv
app = Flask(__name__)

print('sfjkahfksdajhfhdhadahfjljljljljlsd')

def db_connect():
    global connection
    connection = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                                 user='b263072c1ab18d',
                                 password='e4aaaba1',
                                 db='heroku_594ae4223a52c95',
                                 #charset='urf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

@app.route('/a')
def about():
    return render_template('home.html')

@app.route('/players')
def index():
    db_connect()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM all_players"
        cursor.execute(sql)
        result = cursor.fetchall()
    connection.commit()
    connection.close()

    return render_template("players.html",
                           all_players=result)

@app.route('/index')
def connect_test():
    with connection.cursor() as cursor:
        sql="SELECT * FROM test WHERE gender=%s"
        cursor.execute(sql,('male'))
        result=cursor.fetchone()
    return (f"<h1>Hello, {result['name']}!<h1>")

#@app.route('/')
@app.route('/')
def teams():
    national=[]
    nation_dict=dict()
    with open('Official.csv', newline="") as file:
        rows=csv.reader(file)
        for elem in rows:
            national.append(elem)
        countries = national[1:13]

        for team in countries:
            nation_dict[team[0]] = team[1:]
    return render_template("teams.html", countries = nation_dict)

@app.route('/teams/<nteam>')
def national(nteam):
    db_connect()
    national=[]
    nation_dict=dict()
    with open('Official.csv', newline="") as file:
        rows=csv.reader(file)
        for elem in rows:
            national.append(elem)
        countries = national[1:13]

        for team in countries:
            while "" in team:
                team.remove("")
            nation_dict[team[0]] = team[1:]
        sql_str=""
        for member in nation_dict[nteam]:
            sql_str+=f'Nation = "{member}" OR '
        sql_str=sql_str[:-4]

        position=[['GK'],['LB','CB','RB'],['CAM','CM','CDM','LM','RM'],['LW','RW','ST','CF']]
        groups = ["Goalkeepers","Defenders","Midfielders","Attackers"]
        results = []
        for poses in position:
            sql_pos = ""
            for pos in poses:
                sql_pos += f'Position = "{pos}" OR '
            sql_pos = sql_pos[:-4]

            with connection.cursor() as cursor:
                sql=f"SELECT * FROM all_players WHERE Owner = 'Darrell' AND ({sql_str}) AND ({sql_pos})"
                cursor.execute(sql)
                result=cursor.fetchall()
                results.append(result)
            connection.commit()
    return render_template("national.html", results=results, groups=groups)

@app.route('/user/<username>')
def user(username):
    return "<h1>User %s</h1>"%escape(username)

@app.route('/user/<int:post_id>')
def post(post_id):
    return "<h1>User %d</h1>"%post_id



if __name__ == '__main__':
    app.run(debug=True)