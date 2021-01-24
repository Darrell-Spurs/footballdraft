import pymysql


class DbFunctions:
    def __init__(self):
        self.connection = None
        self.db_connect()

    def db_connect(self):
        self.connection = pymysql.connect(host ='us-cdbr-east-02.cleardb.com',
                                         user ='b263072c1ab18d',
                                         password ='e4aaaba1',
                                         db='heroku_594ae4223a52c95',
                                         # charset='urf8mb4',
                                         cursorclass = pymysql.cursors.DictCursor)

    # execute sql to get db data
    def db_control(self, sql, commit=False, fetch="", close=True):
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            if commit:
                self.connection.commit()
            if fetch == "one":
                data = cursor.fetchone()
                return data
            elif fetch == "all":
                data = cursor.fetchall()
                return data
        if close:
            print(">>>>")
            self.connection.close()
        return None

    # add player to national team
    def add_to_nation(self, nteam, action_name):
        sql = "UPDATE all_players SET NATIONAL='%s' WHERE ID=%s" % (nteam, action_name)
        self.db_control(sql, commit=True)

    # remove player from national team
    def del_from_nation(self,action_name):
        sql = "UPDATE all_players SET NATIONAL=NULL WHERE ID=%s" % (action_name)
        self.db_control(sql, commit=True)

    # fetch data of player profile page from db
    def get_profile(self, name):
        with self.connection.cursor() as cursor:
            sql = f"SELECT * FROM stats WHERE player='{name}'"
            print(sql)
            cursor.execute(sql)
            profile = cursor.fetchone()
            vals = []
            for val in profile.values():
                vals.append(val)
        return vals


class GenFunctions:
    def __init__(self):
        self.ALLOWED_EXTENTION = {'jpg', 'png', 'jpeg'}

    # upload
    def allowed_files(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENTION

    # just functions
    def modify_num(self, a):
        if a > 10:
            return str(a)
        return "0" + str(a)

    def modify_date(self,date):
        y = date[0]
        m = date[1]
        d = date[2]
        day = ""
        for elem in map(self.modify_num, [y, m, d]):
            day += elem
        return day

    def full_name(self,name):
        name = name.replace("_"," ")
        return name