from flask import Flask, render_template, request, redirect, session
import random
import sqlite3

app = Flask(__name__)
app.secret_key = "auction_secret"

# -------------------------
# DATABASE SETUP
# -------------------------

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        name TEXT,
        userid TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# PLAYER DATABASE
# -------------------------

database = {
"India":{
"Batsman":["Virat Kohli","Rohit Sharma","Shubman Gill","KL Rahul","Suryakumar Yadav"],
"Bowler":["Jasprit Bumrah","Mohammed Shami","Bhuvneshwar Kumar","Mohammed Siraj","Yuzvendra Chahal"],
"All-Rounder":["Hardik Pandya","Ravindra Jadeja","Axar Patel","Shardul Thakur","Washington Sundar"],
"Wicket-Keeper":["MS Dhoni","Rishabh Pant","Ishan Kishan","Sanju Samson","KL Rahul WK"]
},
"Australia":{
"Batsman":["Steve Smith","David Warner","Marnus Labuschagne","Travis Head","Aaron Finch"],
"Bowler":["Pat Cummins","Mitchell Starc","Josh Hazlewood","Adam Zampa","Mitchell Swepson"],
"All-Rounder":["Glenn Maxwell","Marcus Stoinis","Cameron Green","Mitchell Marsh","Sean Abbott"],
"Wicket-Keeper":["Alex Carey","Matthew Wade","Josh Inglis","Tim Paine","Peter Handscomb"]
}
}

players={}
last_bidder="None"

# -------------------------
# LOGIN PAGE
# -------------------------

@app.route('/')
def login_page():
    return render_template("login.html")

# -------------------------
# LOGIN
# -------------------------

@app.route('/login',methods=['POST'])
def login():

    uid=request.form['userid']
    password=request.form['password']

    conn=sqlite3.connect("users.db")
    c=conn.cursor()

    c.execute("SELECT * FROM users WHERE userid=? AND password=?",(uid,password))
    user=c.fetchone()

    conn.close()

    if user:
        session["user"]=user[0]
        return redirect("/country")

    return "Invalid login"

# -------------------------
# REGISTER PAGE
# -------------------------

@app.route('/register')
def register_page():
    return render_template("register.html")

# -------------------------
# REGISTER USER
# -------------------------

@app.route('/register_user',methods=['POST'])
def register_user():

    name=request.form['name']
    userid=request.form['userid']
    password=request.form['password']

    if len(userid)!=5:
        return "ID must be 5 digits"

    conn=sqlite3.connect("users.db")
    c=conn.cursor()

    try:
        c.execute("INSERT INTO users VALUES(?,?,?)",(name,userid,password))
        conn.commit()
    except:
        return "User already exists"

    conn.close()

    return redirect("/")

# -------------------------
# COUNTRY PAGE
# -------------------------

@app.route('/country')
def country():

    if "user" not in session:
        return redirect("/")

    countries=database.keys()

    return render_template("country.html",countries=countries)

# -------------------------
# PLAYER TYPE
# -------------------------

@app.route('/type',methods=['POST'])
def type_page():

    country=request.form['country']
    types=database[country].keys()

    return render_template("type.html",types=types,country=country)

# -------------------------
# PLAYERS PAGE
# -------------------------

@app.route('/players',methods=['POST'])
def player_page():

    country=request.form['country']
    ptype=request.form['ptype']

    player_list=database[country][ptype]

    player_data={}

    for p in player_list:
        player_data[p]=random.randint(50000,100000)

    return render_template("players.html",players=player_data)

# -------------------------
# AUCTION PAGE
# -------------------------

@app.route('/auction')
def auction():

    player=request.args.get("player")
    price=int(request.args.get("price"))

    players[player]=price

    return render_template("auction.html",players=players,last=last_bidder,error=None)

# -------------------------
# BID
# -------------------------

@app.route('/bid',methods=['POST'])
def bid():

    global last_bidder

    player=request.form['player']
    new_bid=int(request.form['bid'])

    if new_bid<=players[player]:

        return render_template(
        "auction.html",
        players=players,
        last=last_bidder,
        error="Price should be higher than the current bid"
        )

    players[player]=new_bid
    last_bidder=session["user"]

    return render_template(
    "auction.html",
    players=players,
    last=last_bidder,
    error=None
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)