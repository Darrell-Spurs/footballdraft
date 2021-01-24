# import modules
import pymysql
from flask import Flask, request, render_template, redirect, flash
from flask_socketio import SocketIO, emit
import time
import json
import csv
import os
from werkzeug.utils import secure_filename
from werkzeug.middleware.shared_data import SharedDataMiddleware
from func import DbFunctions, GenFunctions
# set app
app = Flask(__name__)

# env variables
UPLOAD_FOLDER = r"C:\Users\darre\PycharmProjects\heroku\static\players"
app.jinja_env.add_extension('jinja2.ext.do')
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.add_url_rule('/upload/<filename>', 'uploaded_file', build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploadfile': app.config['UPLOAD_FOLDER']
})

# set socket
async_mode = "threading"
io = SocketIO(app=app, async_mode=async_mode)

# home page TODO: add more info and new, transactions, etc.
@app.route('/')
def about():
    return render_template('home.html')

# draft list TODO: beautify the list, pagination
@app.route('/players')
def index():
    db = DbFunctions()
    player_list = db.db_control("SELECT * FROM all_players", fetch="all")
    return render_template("players.html",
                           all_players=player_list)

# draft result of each round TODO: bootstrap grid system
@app.route('/round/<r>')
def get_round(r):
    db = DbFunctions()
    # get player info
    sql = f"SELECT ID,Player,Position,Club,Nation,Age FROM all_players WHERE ROUND={r}"
    player_list = db.db_control(sql, fetch="all")
    for elem in player_list:
        # club name shouldn't have spaces because it is used to access logo file
        elem['Club'] = elem['Club'].replace(" ", "_")
    return render_template('rounds.html', r=int(r), result=player_list)

# national teams
# TODO: grid system, more info in the info page
# TODO: csv to db?? (optional) or at least organize the file
@app.route('/teams')
def teams():
    national_team = []
    nation_dict = dict()
    with open('Official.csv', newline="") as file:
        rows = csv.reader(file)
        for elem in rows:
            national_team.append(elem)
        countries = national_team[1:13]

        for team in countries:
            nation_dict[team[0]] = team[1:]

    return render_template("teams.html", countries=nation_dict)

# show selected national team player list
@app.route('/teams/<nteam>')
def national(nteam):
    db = DbFunctions()
    national_team = []
    nation_dict = dict()

    # read countries #TODO: from db?
    with open('Official.csv', newline="") as file:
        rows = csv.reader(file)
        for elem in rows:
            national_team.append(elem)
        countries = national_team[1:13]

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

            sql_find_player = f"SELECT * FROM all_players WHERE Owner = 'Darrell' AND ({sql_str}) AND ({sql_pos})"
            list_of_one_cat = db.db_control(sql_find_player)
            results.append(list_of_one_cat)
    return render_template("national.html", results=results, groups=groups, nteam=nteam)

# real time transactions TODO: scrape transfer market
@app.route('/transactions/real')
def transactions_real():
    return render_template('transaction.html')

# transaction records TODO: set pagination, sort with types
@app.route('/transactions/records')
def transactions_records():

    db = DbFunctions()

    # get all trade records
    sql_trade = "SELECT Time,Number,Player1,Player2 FROM trans_records WHERE type='Trade'"
    trades = db.db_control(sql_trade, fetch="all")
    print(trades)

    # trade list format change (player 1, player 2)
    i = 0
    for note in trades:
        sql1 = f"SELECT Position, Club, Nation FROM all_players WHERE Player='{note['Player1']}'"
        one = db.db_control(sql1, fetch="one")
        print(one)
        trades[i].update({"Player1": {"Name": trades[i]["Player1"], "Pos": one["Position"], "Club": one["Club"],
                                      "Nation": one["Nation"]}})

        sql2 = f"SELECT Position, Club, Nation FROM all_players WHERE Player='{note['Player2']}'"
        two = db.db_control(sql2, fetch="one")
        trades[i].update({"Player2": {"Name": trades[i]["Player2"], "Pos": two["Position"], "Club": two["Club"],
                                      "Nation": two["Nation"]}})
        trades[i].update({"Date": trades[i]["Time"]})
        i += 1

    # get all drop and add records
    sql_dna = "SELECT Time,Player1,Player2 FROM trans_records WHERE type='Add'"
    dnas = db.db_control(sql_dna, fetch="all")

    i = 0

    # alter list format
    for note in dnas:
        sql1 = f"SELECT Position, Club, Nation FROM dropped_players WHERE Name='{note['Player1']}'"
        one = db.db_control(sql1, fetch="one", close=False)
        dnas[i].update({"Player1": {"Name": dnas[i]["Player1"], "Pos": one["Position"], "Club": one["Club"],
                                    "Nation": one["Nation"]}})

        sql2 = f"SELECT Position, Club, Nation FROM all_players WHERE Player='{note['Player2']}'"
        two = db.db_control(sql2, fetch="one")
        dnas[i].update({"Player2": {"Name": dnas[i]["Player2"], "Pos": two["Position"], "Club": two["Club"],
                                    "Nation": two["Nation"]}})
        dnas[i].update({"Date": dnas[i]["Time"]})

        i += 1

    print(dnas)

    return render_template('trans_record.html', trades=trades, dropnadd=dnas)

# tool for add and drop/ trade
# TODO: file update to backend? (admin only)
@app.route('/transactions/tool', methods=["GET", "POST"])
def transactions_tool():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No Files")
            return redirect(request.url)
        file = request.files['file']
        if file == "":
            flash("Empty")
            return redirect(request.url)
        if file and GenFunctions().allowed_files(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            print(path)
            file.save(path)
            return redirect(request.url)
    return render_template('transaction.html')


@app.route("/profile/<name>")
def profile(name):

    db = DbFunctions()
    
    name = GenFunctions().full_name(name)
    print(name)
    
    stats = db.get_profile(name)
    return render_template("player_profile.html", name=name, stats=stats)

# test on connection
@io.on('connect')
def io_connect():
    print('socket connected')

# test on disconnection
@io.on('disconnect')
def io_disconnect():
    print('socket disconnected')

# find player in home page #TODO: get profile
@io.on('home_search')
def home_search(msg):
    db = DbFunctions()
    print('received', msg)
    received = msg['data']
    
    # find target player
    sql = f"SELECT * FROM all_players WHERE Player LIKE '%{received}%'"
    search_result = db.db_control(sql, fetch="all")
    search_result = json.dumps(search_result)
    
    emit('home_result', {'data': search_result})
    print(search_result)

# search player in squad builder
@io.on('builder_search')
def home_search(msg):
    
    db = DbFunctions()
    print('received', msg)
    received = msg['data']

    # find target player
    sql = f"SELECT * FROM all_players WHERE Player LIKE '%{received}%'"
    search_result = db.db_control(sql, fetch="all")
    search_result.insert(0, {'pos': msg['pos'][3:]})
    search_result = json.dumps(search_result)

    # send message of pos and player name to frontend
    emit('builder_result', {'data': search_result})
    print(search_result)

# save squad to db
@io.on("save_squad")
def add_add_squad(msg):
    db = DbFunctions()
    received = msg['players']
    try:
        received = tuple(received)
        sql = f'''INSERT INTO squads (NAME,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14,P15,P16,P17,P18)
              VALUES {received}'''
        db.db_control(sql, commit=True)

    except pymysql.err.ProgrammingError:
        for i in range(len(received)):
            if received[i] == 'd Outline':
                received[i] = 0
            received = tuple(received)
        sql = f'''INSERT INTO squads (NAME,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14,P15,P16,P17,P18)
                VALUES {received}'''
        db.db_control(sql, commit=True)

# alter db while getting message
@io.on('natTeam_Add')
def nat_team_add(msg):
    db = DbFunctions()
    db.add_to_nation(msg['nation'], msg['player'])
    print(msg['player'], msg['nation'])

# alter db while getting message
@io.on('natTeam_Del')
def nat_team_del(msg):
    db = DbFunctions()
    db.del_from_nation(msg['player'])
    print(msg['player'])
    emit("nat_added")

# update db on receiving trade message
@io.on('trade')
def trade(msg):

    db = DbFunctions()

    # get received variables
    print('received:', msg)
    requester = msg['req']
    trade_out = msg['out']
    trade_in = msg['tin']

    # check the receiver
    receiver = ""
    if requester == "Ben":
        receiver = "Darrell"
    else:
        receiver = "Ben"

    # alter db and add record to transaction table
    update1 = "UPDATE all_players SET Owner='%s' WHERE Player='%s'" % (receiver, trade_out)
    db.db_control(update1, close=False)

    update2 = "UPDATE all_players SET Owner='%s' WHERE Player='%s'" % (requester, trade_in)
    db.db_control(update2, close=False)

    record_table = f"INSERT INTO trans_records(Player1,Player2,Type) VALUES('{trade_out}','{trade_in}','Trade')"
    db.db_control(record_table, commit=True)

# add and drop player
@io.on('pick')
def pick(msg):

    db = DbFunctions()

    # get received variables
    print("received:", msg)
    drop = msg['drop']
    add = msg['add']
    position = msg['pos']
    nation = msg['nat']

    # drop player
    drop_sql = f"SELECT ID,Position,Club,Nation FROM all_players WHERE Player='{drop}'"
    dropped_player = db.db_control(drop_sql, fetch="one", close=False)

    dropped_id = dropped_player['ID']

    add_sql = f"UPDATE all_players SET Player='{add}',Position='{position}',Nation='{nation}' WHERE ID={dropped_id}"
    print(add_sql)
    db.db_control(drop_sql, close=False)

    # add dropped player to db to keep his data
    add_to_dropped = f"INSERT INTO dropped_players(Name,Club,Nation,Position)" \
                     f" VALUES('{drop}','{dropped_player['Club']}'," \
                     f"'{dropped_player['Nation']}','{dropped_player['Position']}')"
    db.db_control(add_to_dropped, close=False)

    date = time.localtime()
    day = GenFunctions().modify_date(date)

    transfer_order_sql = "SELECT MAX(Number) FROM trans_records" \
                         "WHERE Type='Add'"
    transfer_order = db.db_control(transfer_order_sql, fetch="one", close=False)['MAX(Number)']

    add_to_record = f"INSERT INTO trans_records " \
                    f"(Number,Player1,Player2,Type,Time) " \
                    f"VALUES('{str(int(transfer_order) + 1)}'," \
                    f"'{drop}','{add}','Add',{day})"
    db.db_control(add_to_record, commit=True)

    print(add_to_record)


# suggest player while searching
@io.on('suggest')
def suggest(msg):
    db = DbFunctions()
    try:
        sug = msg['sug']
        id = msg['field']
        suggest_sql = f"SELECT player,club FROM all_players " \
                      f"WHERE player LIKE '%{sug}%';"
        suggest_result = db.db_control(suggest_sql, fetch="all")
        print("emitted")
        emit('sug_result', {'result': suggest_result, 'ID': id})
    except:
        pass


if __name__ == '__main__':
    io.run(app, debug=True)
