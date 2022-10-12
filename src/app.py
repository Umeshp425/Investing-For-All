import os
import psycopg2
from flask import Flask, g, render_template, redirect, url_for, request, session
import datetime
import json

app = Flask(__name__)
app.secret_key = 'secret key'
date = datetime.datetime(2020, 5, 17)
dateformat = '%Y_%m_%d'

class User:
    def __init__(self, id, username, password, name ,email):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.email = email

    def __repr__(self):
        return f'<User: {self.username}>'

def get_db_connection():
    conn = psycopg2.connect(
        host = "10.17.10.70",
        port=5432,
        database = "group_13",
        user = "group_13",
        password = "QcNtcHm7Hmg9q"
    )
    return conn

@app.before_request
def before_request():
    g.user = None
    if session and session['user_id']:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * from users where userid = '{}'".format(session['user_id']))
        items = cur.fetchone()
        if (items):
            g.user = User(id=items[0], username=items[1], password=items[2], name=items[3], email=items[4])

@app.route('/')
def index():
    #top_stokes
    # print(g.user.username)
    d = datetime.timedelta(days = 10)
    day_10_before=date-d
    print(date,day_10_before)
    query="select f1.symbol, f2.close-f1.close as change, ((f2.close-f1.close)/f1.close)*100 as perchange\
        from\
            (select symbol,Date,close\
            from nifty50_all\
            where Date='{}') as f1\
            ,(select symbol,Date,close\
            from nifty50_all\
            where Date='{}') as f2 \
            where f1.symbol=f2.symbol \
        order by change desc\
        limit 10;"
    
    conn = get_db_connection()
    cur = conn.cursor()    
    cur.execute(query.format(day_10_before,date))
    top_stoks = cur.fetchall()

    #nifty
    query="select f1.sum, (((f1.sum-f2.sum)/f1.sum)*100) as perchange\
        from \
            (select Date,sum(close)\
                from nifty50_all\
                group by Date) as f1,\
        \
            (select Date,sum(close)\
                from nifty50_all\
                group by Date) as f2\
        where f1.Date='{}' and f2.Date='{}'"

    d = datetime.timedelta(days = 1)
    day_1_before=date-d
    cur.execute(query.format(date,day_1_before))
    nifty = cur.fetchone()

    if not session: 
        return render_template("index.html", top_stoks = top_stoks, nifty = nifty, user = {'username':'guest_user', 'is_authenticated':False})
    else:
        return render_template("index.html", top_stoks = top_stoks, nifty = nifty, user = {'username':g.user.username, 'is_authenticated':True})


@app.route('/search', methods=['POST'])
def search():
    st = request.form['search']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select * from stock_metadata where symbol='{st.upper()}'")
    ans = cur.fetchall()
    if not ans:
        return redirect(url_for("index"))
    return redirect(url_for('stock',stockname=st))

@app.route('/stock')
def stock():
    #data query
    stockname=request.args.get('stockname')
    conn = get_db_connection()
    cur = conn.cursor()
    query="SELECT * from "+stockname+" where symbol = '{}' and Date <= '{}'"
    cur.execute(query.format(stockname.upper(),str(date)))
    data = cur.fetchall()
    
    #low,high queries
    query="SELECT * from "+stockname+" where symbol = '{}' and Date = '{}'"
    cur.execute(query.format(stockname.upper(),date))
    current=cur.fetchall()

    #low52,high52 queries
    query="SELECT symbol,max(high) from "+stockname+" where symbol = '{}' and Date <= '{}' and Date > '{}' group by symbol"
    cur.execute(query.format(stockname.upper(),date,datetime.datetime(2019,5,17)))
    high52=cur.fetchone()[1]
    query="SELECT symbol,min(low) from "+stockname+" where symbol = '{}' and Date <= '{}' and Date > '{}' group by symbol"
    cur.execute(query.format(stockname.upper(),date,datetime.datetime(2019,5,17)))
    low52=cur.fetchone()[1]
    if not session: 
        return render_template("stock.html",date=date,stockname=stockname,current=current,low52=low52,high52=high52,data=data,user = {'username':'guest_user', 'is_authenticated':False})
    else:
        return render_template("stock.html",date=date,stockname=stockname,current=current,low52=low52,high52=high52,data=data,user = {'username':g.user.username, 'is_authenticated':True})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        conn = get_db_connection()
        cur = conn.cursor()
        id = request.form['UserId']
        password = request.form['Password']
        query = "SELECT * from users where username = '{}' and password = '{}'"
        cur.execute(query.format(id,password))
        items = cur.fetchone()
        if not items:
            return render_template('login.html', error="Invalid credentials")
        user = User(id=items[0], username=items[1], password=items[2], name=items[3], email=items[4])
        session['user_id'] = user.id
        return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    conn = get_db_connection()
    cur = conn.cursor()
    name = request.form['name']
    id = request.form['UserId']        #unique
    password = request.form['Password']
    email = request.form['Email']
    query = "SELECT * from users where username = '{}'"
    cur.execute(query.format(id))
    ans = cur.fetchone()
    if ans:
        return render_template('login.html', error="UserID already taken choose another userID")
    else:
        query = "INSERT INTO users VALUES((select count(*)+1 from users), '{}','{}','{}','{}')"
        cur.execute(query.format(id, password, name, email))
        conn.commit()
        return render_template('login.html', error='Succesfully Registered. Login now')

@app.route('/searchStockes', methods=['GET','POST'])
def search_stokes():
    if not session: 
        return redirect(url_for('login'))
    print(request.method)
    if request.method=='POST':
        stockname = request.form['search']
        return redirect(url_for('buy',stockname=stockname))
    return render_template("searchstock.html", user = {'username':g.user.username, 'is_authenticated':True})

@app.route('/buy', methods=['GET','POST'])
def buy():
    if not session:
        return redirect(url_for('login'))
    if request.method=='POST':
        quantity = int(request.form['search'])
        temp=0
        if(quantity<0): 
            temp=1
        id = request.args.get('id')
        stockname=request.args.get('stockname')
        # print(quantity,id,type(quantity), type(id), id=='0', id==0)
        if(id=='0'):               #sell
            quantity=0-quantity          #sell
        print(quantity)
        transactionid_query=f"select max(transactionid) from transactions"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(transactionid_query)
        
        transactionid=cur.fetchone()
        if transactionid:
            transactionid=transactionid[0]+1
        else:
            transactionid=1

        query = f"select close from {stockname} where Date='{date}'"
        cur.execute(query)
        currentprice=cur.fetchone()[0]

        #check portfolio
        query=f"select * from portfolios where userid={g.user.id} and symbol='{stockname.upper()}'"
        cur.execute(query)
        items=cur.fetchall()
        if(items):
            old_hold=items[0][2]
            if(temp):
                return render_template("buy_sell.html", stockname=stockname, quantity=old_hold, currentprice=currentprice, user = {'username':g.user.username, 'is_authenticated':True}, error="Please enter positive value")
            print(old_hold+quantity)
            if old_hold+quantity<0:
                return render_template("buy_sell.html", stockname=stockname, quantity=old_hold, currentprice=currentprice, user = {'username':g.user.username, 'is_authenticated':True}, error="insufficient stocks")
            elif old_hold+quantity==0:
                query =f"delete from portfolios where userid={g.user.id} and symbol='{stockname.upper()}'"
            else:
                query=f"update portfolios set units = '{old_hold+quantity}' where userid={g.user.id} and symbol='{stockname.upper()}'"
            cur.execute(query)
            #update
        else:
            if(temp):
                return render_template("buy_sell.html", stockname=stockname, quantity=0, currentprice=currentprice, user = {'username':g.user.username, 'is_authenticated':True}, error="Please enter positive value")
            if id=='0':
                return render_template("buy_sell.html", stockname=stockname, quantity=0, currentprice=currentprice, user = {'username':g.user.username, 'is_authenticated':True}, error="insufficient stocks")
            query=f"insert into portfolios (userid,symbol,units) VALUES({g.user.id},'{stockname.upper()}',{quantity})"
            cur.execute(query)
            #insert
    
        insert_query=f"insert into transactions (transactionid,date,userid,symbol,units)"\
                    f"VALUES({transactionid+1},'{date}',{g.user.id},'{stockname.upper()}',{quantity})"
        cur.execute(insert_query)
        conn.commit()

        print(quantity)
        return redirect(url_for("profile"))

    conn = get_db_connection()
    cur = conn.cursor()
    stockname=request.args.get('stockname')
    cur.execute(f"select * from stock_metadata where symbol='{stockname.upper()}'")
    ans = cur.fetchall()
    if not ans:
        return render_template("searchstock.html", user = {'username':g.user.username, 'is_authenticated':True}, error="stockname does exits please enter a valid stockname")
    query = f"select * from portfolios where symbol='{stockname.upper()}' and userid={g.user.id}"
    cur.execute(query)
    items = cur.fetchone()
    query = f"select close from {stockname} where Date='{date}'"
    cur.execute(query)
    currentprice=cur.fetchone()[0]
    quantity=0
    if items:
        quantity=items[2]
    print(items,quantity)
    return render_template("buy_sell.html", stockname=stockname, quantity=quantity, currentprice=currentprice, user = {'username':g.user.username, 'is_authenticated':True}, error="Enter quantity to buy/sell")

@app.route('/add_to_watch_list', methods=['POST'])
def add_watch():
    if not session:
        return redirect(url_for('login'))
    stockname = request.form['search']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select * from stock_metadata where symbol='{stockname.upper()}'")
    ans = cur.fetchall()
    if not ans:
        return render_template("searchstock.html", user = {'username':g.user.username, 'is_authenticated':True}, error="stockname does not exits please enter a valid stockname")

    cur.execute(f"select * from watchlists where userid={g.user.id} and symbol='{stockname.upper()}'")
    items = cur.fetchall()
    if not items:
        cur.execute(f"insert into watchlists (userid,symbol) VALUES({g.user.id},'{stockname.upper()}')")
        conn.commit()

    # cur.execute(f"insert into watchlists (userid,symbol) VALUES({g.user.id},'{stockname.upper()}')")
    # conn.commit()

    print(stockname)
    return redirect(url_for('profile'))
    
@app.route('/add_to_watchList')
def add_to_watch():
    if not session:
        return redirect(url_for('login'))
    stockname = request.args.get('stockname')
    print(stockname)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select * from watchlists where userid={g.user.id} and symbol='{stockname.upper()}'")
    items = cur.fetchall()
    if not items:
        cur.execute(f"insert into watchlists (userid,symbol) VALUES({g.user.id},'{stockname.upper()}')")
        conn.commit()

    print(stockname)
    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if not session: 
        return redirect(url_for('login'))

    d = datetime.timedelta(days = 1)
    date_yesterday=date-d

    watchListQuery =    f'with todayVals as (' \
                        f'  select w.symbol, n.close ' \
                        f'  from watchlists w, nifty50_all n ' \
                        f'  where n.date = \'{date}\' and w.userid = {g.user.id} and w.symbol = n.symbol' \
                        f' ), yestVals as ('\
                        f'  select w.symbol, n.close ' \
                        f'  from watchlists w, nifty50_all n ' \
                        f'  where n.date = \'{date_yesterday}\' and w.userid = {g.user.id} and w.symbol = n.symbol' \
                        f' ) ' \
                        f'select t.symbol, t.close, (t.close-y.close)*100.0/y.close as change ' \
                        f'from todayVals t, yestVals y ' \
                        f'where t.symbol = y.symbol'

    cur.execute(watchListQuery)
    watchlist = cur.fetchall()
    
    currentValue = [9235.3, -4.5]


    #add refreshing procedure
    holdingsViewQuery = f'create or replace view holdings_{g.user.id}_{date.strftime(dateformat)} ' \
                        f'as ' \
                        f'select p.symbol, (n.close * p.units) as value, p.units, n.close ' \
                        f'from  portfolios p, nifty50_all n ' \
                        f'where n.date = \'{date}\' and p.userid = {g.user.id} and p.symbol = n.symbol'

    cur.execute(holdingsViewQuery)

    # holdingsRuleQuery = f'create or replace rule holdings_{g.user.id}_{date.strftime(dateformat)}_insert AS '\
    #                     f'on insert to portfolios '\
    #                     f'where new.userid = {g.user.id} ' \
    #                     f'do also refresh materialized view holdings_{g.user.id}_{date.strftime(dateformat)}; ' \
    #                     f'create or replace rule holdings_{g.user.id}_{date.strftime(dateformat)}_update AS '\
    #                     f'on update to portfolios '\
    #                     f'where new.userid = {g.user.id} ' \
    #                     f'do also refresh materialized view holdings_{g.user.id}_{date.strftime(dateformat)}; ' \
    #                     f'create or replace rule holdings_{g.user.id}_{date.strftime(dateformat)}_delete AS '\
    #                     f'on delete to portfolios '\
    #                     f'where new.userid = {g.user.id} ' \
    #                     f'do also refresh materialized view holdings_{g.user.id}_{date.strftime(dateformat)}; '
    # cur.execute(holdingsRuleQuery)

    holdingsTableQuery = f'select * from holdings_{g.user.id}_{date.strftime(dateformat)}'
    
    cur.execute(holdingsTableQuery)
    holdings = cur.fetchall()

    holdingsValueQuery =    f'with yestVals as (' \
                            f'  select p.symbol, (n.close * p.units) as value ' \
                            f'  from  portfolios p, nifty50_all n ' \
                            f'  where n.date = \'{date_yesterday}\' and p.userid = {g.user.id} and p.symbol = n.symbol' \
                            f'), todaySum as (' \
                            f'  select sum(h.value) as val ' \
                            f'  from holdings_{g.user.id}_{date.strftime(dateformat)} h' \
                            f'), yestSum as (' \
                            f'  select sum(value) as val ' \
                            f'  from yestVals)' \
                            f'select t.val, (t.val-y.val)*100/y.val as change from todaySum t, yestSum y'
                    
    cur.execute(holdingsValueQuery)
    currentValue = cur.fetchone()
    if not currentValue[0]:
        currentValue=[0,0]
    d = datetime.timedelta(days = 365)
    date_1year = date-d


    fstring = '%Y-%m-%d'
    historyDataQuery = \
    f'with currentPortfolio as (' \
    f'  select cast(\'{date.strftime(fstring)}\' as date) as date, symbol, units' \
    f'  from holdings_{g.user.id}_{date.strftime(dateformat)} ' \
    f'), transactionUnits as (' \
    f'  select t.date, t.symbol, sum(t.units) as units ' \
    f'  from transactions t ' \
    f'  where t.userid = {g.user.id} ' \
    f'  and t.date > (select distinct date-365 from currentPortfolio) ' \
    f'  group by t.date, t.symbol' \
    f'), allDates as (' \
    f'  select date, allSymbols.symbol from ongc, (select distinct symbol from transactionUnits) as allSymbols' \
    f'  where date <= (select distinct date from currentPortfolio) and date > (select distinct date - 365 from currentPortfolio)' \
    f'), transactionPadded as (' \
    f'  select a.date-1 as date, a.symbol, (case when t.units is NULL then 0 else t.units end) ' \
    f'  from transactionUnits t ' \
    f'  right outer join allDates a ' \
    f'  on t.date = a.date and t.symbol = a.symbol' \
    f'), transactionCumulative as (' \
    f'  select t.date, t.symbol, sum(t.units) ' \
    f'                           over (partition by t.symbol order by t.date desc) as units ' \
    f'  from transactionPadded t' \
    f'), histPortfolios as (' \
    f'  select t.date, c.symbol, (case when c.units is NULL then 0 else c.units end) - ' \
    f'                           (case when t.units is NULL then 0 else t.units end) as units ' \
    f'  from currentPortfolio c' \
    f'  full outer join transactionCumulative t ' \
    f'  on t.symbol = c.symbol ' \
    f')' \
    f'select h.date, sum(h.units*n.close) as value ' \
    f'from histPortfolios h, nifty50_all n ' \
    f'where h.date = n.date and h.symbol = n.symbol ' \
    f'group by h.date ' \
    f'order by h.date asc'

    cur.execute(historyDataQuery)
    historyData = cur.fetchall()
    
    return render_template('profile.html',
                            user = {'username':g.user.username, 'is_authenticated':True}, 
                            watchlist = watchlist,
                            currentValue=currentValue, 
                            holdings=holdings,
                            historyData=historyData)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(error):
    return "Error while loading the data"

@app.route('/chk')
def chk():
    conn = get_db_connection()
    cur = conn.cursor()
    print('Users')
    cur.execute("select * from watchlists;")
    st = cur.fetchall()
    for line in st:
        print(line)
    print('transactions')
    cur.execute("select * from transactions")
    st = cur.fetchall()
    for line in st:
        print(line)
    print("profile")
    cur.execute("select * from portfolios")
    st = cur.fetchall()
    for line in st:
        print(line)
    
    conn.commit()
    return redirect(url_for('index'))
    # cur.execute('create table if not exists users(\
    #     uid text,\
    #     name text,\
    #     password text,\
    #     email text,\
    #     bugget bigint\
    #     );\
    # ')

    # cur.execute('select * from pg_tables where schemaname=\'public\';')
    # st = cur.fetchall()
    # for line in st:
    #     print(line)
    # cur.execute('select * from zeel limit 0')
    # colnames = [desc[0] for desc in cur.description]
    # # # print("cur.description", cur.description)
    # # print(colnames)
    # cur.execute('select count(*) from pg_tables where schemaname=\'public\';')
    # st = cur.fetchall()
    # for line in st:
    #     print(line)


    # cur.close()
    # conn.close()
    # return render_template('index.html', stock=st, colnames = colnames)
    # return render_template('index.html')

@app.route('/login_id', methods=["POST"])
def check_login():
    id = request.form['UserId']
    password = request.form['Password']
    print(id,password)


    watchlist = [["TATA MOTORS", 966.3, 2.3], ['FB', 423.4, -53.0], ['WA', 23.0, 1.0], ["TATA MOTORS", 966.3, 2.3], 
                ['FB', 423.4, -53.0], ['WA', 23.0, 1.0], ["TATA MOTORS", 966.3, 2.3], 
                ['FB', 423.4, -53.0], ['WA', 23.0, 1.0], ["TATA MOTORS", 966.3, 2.3], ['FB', 423.4, -53.0], ['WA', 23.0, 1.0]]
    currentValue = [9235.3, -4.5]

    holdings = [["TM", 466.3, 2.3, 466.3/2.3],
                ["WA", 203.3, 3.4, 203.3/3.4], 
                ["GA", 146.3, 3.3, 146.3/3.3], 
                ["BB", 456.3, 7.4, 456.3/7.4], 
                ["MS", 567.3, 2.5, 567.3/2.5], 
                ["JP", 966.3, 7.8, 966.3/7.8]]

    transactions = ['buy TM 1.0', 'buy FB 2.0', 'sell WA 1.0', 'buy BB 10.0', 'sell JP 1.0', 'buy GA 12.0', 'sell BB 13.0', 'buy TM 1.0']

    historyData = []
    with open('history_data.csv', 'r') as f:
        f.readline()
        y = f.readline()
        while y:
            line = y.split(',') 
            historyData.append([line[1], float(line[2].split('\n')[0]), None])
            y=f.readline()
    
    for i in range(len(transactions)):
        historyData[50*i][2] = transactions[i]

    return render_template("profile.html", 
                            user = {'username':id, 'is_authenticated':True}, 
                            watchlist = watchlist,
                            currentValue=currentValue, 
                            holdings=holdings,
                            historyData=historyData)
    # return render_template('profile') # stock=[], colnames=[])


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5013, debug=True)
    # app.run(host='127.0.0.1', port=5024)