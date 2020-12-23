from flask import Flask, request, render_template, url_for, redirect, flash, send_from_directory
from flask_socketio import SocketIO, send, emit
import time
import json
import pymysql
import pymysql.cursors
import csv
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = r"C:\Users\darre\PycharmProjects\heroku\static\players"
ALLOWED_EXTENTION = {'jpg', 'png', 'jpeg'}
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

from werkzeug.middleware.shared_data import SharedDataMiddleware

app.add_url_rule('/upload/<filename>', 'uploaded_file',
                  build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploadfile': app.config['UPLOAD_FOLDER']
})

async_mode = "threading"
io = SocketIO(app=app, async_mode=async_mode)


# io = SocketIO(app=app, async_mode=async_mode)

def db_connect():
    global connection
    connection = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                                 user='b263072c1ab18d',
                                 password='e4aaaba1',
                                 db='heroku_594ae4223a52c95',
                                 # charset='urf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
def r_connect():
    connection = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                                 user='b263072c1ab18d',
                                 password='e4aaaba1',
                                 db='heroku_594ae4223a52c95',
                                 # charset='urf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection
def db_control(connection, sql, commit=False, fetch=0):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        if commit == True:
            connection.commit()
        if fetch == 1:
            return cursor.fetchone()
        elif fetch == 2:
            return cursor.fetchall()
    connection.close()
def add_to_N(nteam, action_name):
    conn = r_connect()
    sql = "UPDATE all_players SET NATIONAL='%s' WHERE ID=%s" % (nteam, action_name)
    db_control(conn, sql, commit=True)
def del_from_N(action_name):
    conn = r_connect()
    sql = "UPDATE all_players SET NATIONAL=NULL WHERE ID=%s" % (action_name)
    db_control(conn, sql, commit=True)
def modify_num(a):
    if a > 10:
        return str(a)
    return "0" + str(a)
def modify_date(date):
    y = date[0]
    m = date[1]
    d = date[2]
    day = ""
    for elem in map(modify_num, [y, m, d]):
        day += elem
    return day
def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTION


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
    conn = r_connect()
    sql = f"SELECT ID,Player,Position,Club,Nation,Age FROM all_players WHERE ROUND={r}"
    result = db_control(conn, sql, fetch=2)
    for elem in result:
        while (elem['Club'].find(" ") != -1):
            f = elem['Club'].find(" ")
            elem['Club'] = elem['Club'][:f] + "_" + elem['Club'][f + 1:]
    return render_template('rounds.html', r=int(r), result=result)


@app.route('/index')
def connect_test():
    with connection.cursor() as cursor:
        sql = "SELECT * FROM test WHERE gender=%s"
        cursor.execute(sql, ('male'))
        result = cursor.fetchone()
        connection.close()
    return (f"<h1>Hello, {result['name']}!<h1>")


@app.route('/teams')
def teams():
    national = []
    nation_dict = dict()
    with open('Official.csv', newline="") as file:
        rows = csv.reader(file)
        for elem in rows:
            national.append(elem)
        countries = national[1:13]

        for team in countries:
            nation_dict[team[0]] = team[1:]

    return render_template("teams.html", countries=nation_dict)


@app.route('/transactions/real')
def transactions_real():
    return render_template('transaction.html')


@app.route('/transactions/records')
def transactions_records():
    conn = r_connect()
    sql_trade = "SELECT Time,Number,Player1,Player2 FROM trans_records WHERE type='Trade'"
    trades = db_control(conn, sql_trade, fetch=2)

    print(trades)

    i = 0
    for note in trades:
        sql1 = f"SELECT Position, Club, Nation FROM all_players WHERE Player='{note['Player1']}'"
        one = db_control(conn, sql1, fetch=1)
        trades[i].update({"Player1": {"Name": trades[i]["Player1"], "Pos": one["Position"], "Club": one["Club"],
                                      "Nation": one["Nation"]}})

        sql2 = f"SELECT Position, Club, Nation FROM all_players WHERE Player='{note['Player2']}'"
        two = db_control(conn, sql2, fetch=1)
        trades[i].update({"Player2": {"Name": trades[i]["Player2"], "Pos": two["Position"], "Club": two["Club"],
                                      "Nation": two["Nation"]}})
        trades[i].update({"Date": trades[i]["Time"]})
        i += 1

    sql_dna = "SELECT Time,Player1,Player2 FROM trans_records WHERE type='Add'"
    dnas = db_control(conn, sql_dna, fetch=2)

    i = 0
    for note in dnas:
        sql1 = f"SELECT Position, Club, Nation FROM dropped_players WHERE Name='{note['Player1']}'"
        one = db_control(conn, sql1, fetch=1)
        dnas[i].update({"Player1": {"Name": dnas[i]["Player1"], "Pos": one["Position"], "Club": one["Club"],
                                    "Nation": one["Nation"]}})

        sql2 = f"SELECT Position, Club, Nation FROM all_players WHERE Player='{note['Player2']}'"
        two = db_control(conn, sql2, fetch=1)
        dnas[i].update({"Player2": {"Name": dnas[i]["Player2"], "Pos": two["Position"], "Club": two["Club"],
                                    "Nation": two["Nation"]}})
        dnas[i].update({"Date": dnas[i]["Time"]})

        i += 1

    print(dnas)

    return render_template('trans_record.html', trades=trades, dropnadd=dnas)


@app.route('/transactions/tool',methods=["GET","POST"])
def transactions_tool():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No Files")
            return redirect(request.url)
        file = request.files['file']
        if file == "":
            flash("Empty")
            return redirect(request.url)
        if file and allowed_files(file.filename):
            filename = secure_filename(file.filename)
            #os.chmod("C:\\",)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            print(path)
            file.save(path)
            return redirect(request.url)
    return render_template('transaction.html')


@app.route('/teams/<nteam>')
def national(nteam):
    db_connect()
    national = []
    nation_dict = dict()

    # read countries
    with open('Official.csv', newline="") as file:
        rows = csv.reader(file)
        for elem in rows:
            national.append(elem)
        countries = national[1:13]

        # get country list from csv
        for team in countries:
            while "" in team:
                team.remove("")
            nation_dict[team[0]] = team[1:]
        sql_str = ""
        # create get sql for searching available players
        for member in nation_dict[nteam]:
            sql_str += f'Nation = "{member}" OR '
        sql_str = sql_str[:-4]

        # classify positions
        position = [['GK'], ['LB', 'CB', 'RB'], ['CAM', 'CM', 'CDM', 'LM', 'RM'], ['LW', 'RW', 'ST', 'CF']]
        groups = ["Goalkeepers", "Defenders", "Midfielders", "Attackers"]
        results = []
        for poses in position:
            sql_pos = ""
            for pos in poses:
                sql_pos += f'Position = "{pos}" OR '
            sql_pos = sql_pos[:-4]  # remove the last 'OR'

            # select players from each category
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM all_players WHERE Owner = 'Darrell' AND ({sql_str}) AND ({sql_pos})"
                cursor.execute(sql)
                result = cursor.fetchall()
                results.append(result)
            connection.commit()
        connection.close()
    return render_template("national.html", results=results, groups=groups, nteam=nteam)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No Files")
            return redirect(request.url)
        file = request.files['file']
        if file == "":
            flash("Empty")
            return redirect(request.url)
        if file and allowed_files(file.filename):
            filename = secure_filename(file.filename)
            #os.chmod("C:\\",)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            print(path)
            file.save(path)
            return redirect(request.url)
    return render_template("upload.html")





@io.on('connect')
def io_connect():
    print('socket connected')


@io.on('disconnect')
def io_disconnect():
    print('socket disconnected')


@io.on('home_search')
def home_search(msg):
    print('Recieved', msg)
    recieved = msg['data']
    db_connect()
    with connection.cursor() as cursor:
        sql = f"SELECT * FROM all_players WHERE Player LIKE '%{recieved}%'"
        cursor.execute(sql)
        result = cursor.fetchall()
        result = json.dumps(result)
        connection.commit()
    connection.close()
    emit('home_result', {'data': result})
    print(result)


@io.on('builder_search')
def home_search(msg):
    print('Recieved', msg)
    recieved = msg['data']
    db_connect()
    with connection.cursor() as cursor:
        sql = f"SELECT * FROM all_players WHERE Player LIKE '%{recieved}%'"
        cursor.execute(sql)
        result = cursor.fetchall()
        result.insert(0, {'pos': msg['pos'][3:]})
        result = json.dumps(result)
        connection.commit()
    connection.close()
    emit('builder_result', {'data': result})
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
                if recieved[i] == 'd Outline':
                    recieved[i] = 0
                recieved = tuple(recieved)
            sql = f'''INSERT INTO squads (NAME,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14,P15,P16,P17,P18)
                    VALUES {recieved}'''
            cursor.execute(sql)
            connection.commit()
    connection.close()


@io.on('natTeam_Add')
def natTeam_Add(msg):
    add_to_N(msg['nation'], msg['player'])
    print(msg['player'], msg['nation'])


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
    print('Recieved:', msg)
    req = msg['req']
    out = msg['out']
    tin = msg['tin']
    db_connect()
    with connection.cursor() as cursor:
        rec = ""
        if req == "Ben":
            rec = "Darrell"
        else:
            rec = "Ben"
        Update1 = "UPDATE all_players SET Owner='%s' WHERE Player='%s'" % (rec, out)
        cursor.execute(Update1)

        Update2 = "UPDATE all_players SET Owner='%s' WHERE Player='%s'" % (req, tin)
        cursor.execute(Update2)

        record_table = f"INSERT INTO trans_records(Player1,Player2,Type) VALUES('{out}','{tin}','Trade')"
        cursor.execute(record_table)

        connection.commit()
    connection.close()


@io.on('pick')
def pick(msg):
    print("Recieved:", msg)
    drop = msg['drop']
    add = msg['add']
    pos = msg['pos']
    nat = msg['nat']
    db_connect()
    with connection.cursor() as cursor:
        drop_sql = f"SELECT ID,Position,Club,Nation FROM all_players WHERE Player='{drop}'"
        cursor.execute(drop_sql)
        fetch_note = cursor.fetchone()

        ID = fetch_note['ID']
        add_sql = f"UPDATE all_players SET Player='{add}',Position='{pos}',Nation='{nat}' WHERE ID={ID}"
        print(add_sql)
        cursor.execute(add_sql)

        add_to_dropped = f"INSERT INTO dropped_players(Name,Club,Nation,Position) VALUES('{drop}','{fetch_note['Club']}','{fetch_note['Nation']}','{fetch_note['Position']}')"
        cursor.execute(add_to_dropped)
        print(add_to_dropped)

        date = time.localtime()
        day = modify_date(date)
        num_sql = "SELECT MAX(Number) FROM trans_records WHERE Type='Add'"
        cursor.execute(num_sql)
        num = cursor.fetchone()['MAX(Number)']

        add_to_record = f"INSERT INTO trans_records (Number,Player1,Player2,Type,Time) VALUES('{str(int(num) + 1)}','{drop}','{add}','Add',{day})"
        cursor.execute(add_to_record)
        print(add_to_record)

        connection.commit()
    connection.close()


@io.on('suggest')
def suggest(msg):
    try:
        sug = msg['sug']
        id = msg['field']
        conn = r_connect()
        sql = f"SELECT player,club FROM all_players WHERE player LIKE '%{sug}%';"
        print("emitted")
        emit('sug_result', {'result': db_control(conn, sql, fetch=2), 'ID': id})
    except:
        pass


if __name__ == '__main__':
    io.run(app, debug=True)
