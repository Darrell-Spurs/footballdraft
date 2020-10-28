from flask import Flask,request,render_template, url_for,redirect
from flask_socketio import SocketIO, send, emit
from markupsafe import escape
import json
import pymysql
import pymysql.cursors
import csv
import time
app = Flask(__name__)

async_mode="threading"
io = SocketIO(app=app, async_mode=async_mode)
#io = SocketIO(app=app, async_mode=async_mode)

def db_connect():
    global connection
    connection = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                                 user='b263072c1ab18d',
                                 password='e4aaaba1',
                                 db='heroku_594ae4223a52c95',
                                 #charset='urf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
def add_to_N(nteam,action_name):
    db_connect()
    with connection.cursor() as cursor:
        sql = "UPDATE all_players SET NATIONAL='%s' WHERE ID=%s" % (nteam, action_name)
        cursor.execute(sql)
        connection.commit()
    connection.close()
def del_from_N(action_name):
    db_connect()
    with connection.cursor() as cursor:
        sql = "UPDATE all_players SET NATIONAL=NULL WHERE ID=%s" % (action_name)
        cursor.execute(sql)
        connection.commit()
    connection.close()

@app.route('/')
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


@app.route('/round/<r>')
def get_round(r):
    db_connect()
    with connection.cursor() as cursor:
        sql = f"SELECT ID,Player,Position,Club,Nation,Age FROM all_players WHERE ROUND={r}"
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.commit()
    connection.close()
    print(type(result[0]))
    for elem in result:
        while (elem['Club'].find(" ") != -1):
            f=elem['Club'].find(" ")
            elem['Club'] = elem['Club'][:f] + "_" + elem['Club'][f + 1:]
    return render_template('rounds.html',r=int(r),result=result)

@app.route('/index')
def connect_test():
    with connection.cursor() as cursor:
        sql="SELECT * FROM test WHERE gender=%s"
        cursor.execute(sql,('male'))
        result=cursor.fetchone()
        connection.close()
    return (f"<h1>Hello, {result['name']}!<h1>")

@app.route('/teams')
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

@app.route('/transactions/real')
def transactions_real():
    return render_template('transaction.html')

@app.route('/transactions/records')
def transactions_records():
    return render_template('transaction.html')

@app.route('/transactions/tool')
def transactions_tool():
    return render_template('transaction.html')

@app.route('/teams/<nteam>')
def national(nteam):
    db_connect()
    national=[]
    nation_dict=dict()

    #read countries
    with open('Official.csv', newline="") as file:
        rows=csv.reader(file)
        for elem in rows:
            national.append(elem)
        countries = national[1:13]

        #get country list from csv
        for team in countries:
            while "" in team:
                team.remove("")
            nation_dict[team[0]] = team[1:]
        sql_str=""
        #create get sql for searching available players
        for member in nation_dict[nteam]:
            sql_str+=f'Nation = "{member}" OR '
        sql_str=sql_str[:-4]

        #classify positions
        position=[['GK'],['LB','CB','RB'],['CAM','CM','CDM','LM','RM'],['LW','RW','ST','CF']]
        groups = ["Goalkeepers","Defenders","Midfielders","Attackers"]
        results = []
        for poses in position:
            sql_pos = ""
            for pos in poses:
                sql_pos += f'Position = "{pos}" OR '
            sql_pos = sql_pos[:-4] #remove the last 'OR'

            #select players from each category
            with connection.cursor() as cursor:
                sql=f"SELECT * FROM all_players WHERE Owner = 'Darrell' AND ({sql_str}) AND ({sql_pos})"
                cursor.execute(sql)
                result=cursor.fetchall()
                results.append(result)
            connection.commit()
        connection.close()
    return render_template("national.html", results=results, groups=groups, nteam=nteam)

@app.route('/user/<username>')
def user(username):
    return "<h1>User %s</h1>"%escape(username)

@app.route('/user/<int:post_id>')
def post(post_id):
    return "<h1>User %d</h1>"%post_id

@io.on('connect')
def io_connect():
    print('socket connected')

@io.on('disconnect')
def io_disconnect():
    print('socket disconnected')

@io.on('home_search')
def home_search(msg):
    print('Recieved',msg)
    recieved = msg['data']
    db_connect()
    with connection.cursor() as cursor:
        sql = f"SELECT * FROM all_players WHERE Player LIKE '%{recieved}%'"
        cursor.execute(sql)
        result = cursor.fetchall()
        result = json.dumps(result)
        connection.commit()
    connection.close()
    emit('home_result',{'data':result})
    print(result)

@io.on('builder_search')
def home_search(msg):
    print('Recieved',msg)
    recieved = msg['data']
    db_connect()
    with connection.cursor() as cursor:
        sql = f"SELECT * FROM all_players WHERE Player LIKE '%{recieved}%'"
        cursor.execute(sql)
        result = cursor.fetchall()
        result.insert(0,{'pos':msg['pos'][3:]})
        result = json.dumps(result)
        connection.commit()
    connection.close()
    emit('builder_result',{'data':result})
    print(result)

@io.on("save_squad")
def add_add_squad(msg):
    recieved = msg['players']
    db_connect()
    with connection.cursor() as cursor:
        try:
            recieved = tuple(recieved)
            sql = f'''INSERT INTO squads (NAME,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14,P15,P16,P17,P18)
                  VALUES {recieved}'''
            cursor.execute(sql)
            connection.commit()
        except:
            for i in range(len(recieved)):
                if recieved[i]=='d Outline':
                    recieved[i]=0
                recieved = tuple(recieved)
            sql = f'''INSERT INTO squads (NAME,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14,P15,P16,P17,P18)
                    VALUES {recieved}'''
            cursor.execute(sql)
            connection.commit()
    connection.close()

@io.on('natTeam_Add')
def natTeam_Add(msg):
    add_to_N(msg['nation'],msg['player'])
    print(msg['player'],msg['nation'])

@io.on('natTeam_Del')
def natTeam_Del(msg):
    del_from_N(msg['player'])
    print(msg['player'])
    emit("nat_added")

@io.on('testtest')
def testtest(msg):
    print(msg)
    emit("nat_deleted")

@io.on('trade')
def trade(msg):
    print('Recieved:',msg)
    req = msg['req']
    out=msg['out']
    tin=msg['tin']
    db_connect()
    with connection.cursor() as cursor:
        rec=""
        if req=="Ben":
            rec="Darrell"
        else:
            rec="Ben"
        Update1 = "UPDATE all_players SET Owner='%s' WHERE Player='%s'"%(rec,out)
        cursor.execute(Update1)

        Update2 = "UPDATE all_players SET Owner='%s' WHERE Player='%s'"%(req,tin)
        cursor.execute(Update2)

        connection.commit()
    connection.close()

@io.on('pick')
def pick(msg):
    print("Recieved:",msg)
    drop=msg['drop']
    add=msg['add']
    pos=msg['pos']
    nat=msg['nat']
    db_connect()
    with connection.cursor() as cursor:
        drop_sql = f"SELECT ID FROM all_players WHERE Player='{drop}'"
        cursor.execute(drop_sql)
        ID = cursor.fetchone()['ID']

        add_sql = f"UPDATE all_players SET Player='{add}',Position='{pos}',Nation='{nat}' WHERE ID={ID}"
        print(add_sql)
        cursor.execute(add_sql)
        connection.commit()
    connection.close()

@io.on('suggest')
def suggest(msg):
    try:
        sug = msg['sug']
        db_connect()
        with connection.cursor() as cursor:
            sql = f"SELECT player,club FROM all_players WHERE player LIKE '%{sug}%';"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)
        connection.close()
        print("emitted")
        emit('sug_result',{'result': result})
    except:
        pass
if __name__ == '__main__':
    io.run(app)