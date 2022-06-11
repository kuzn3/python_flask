from time import sleep
from flask import Flask, redirect, render_template, request, url_for, session, jsonify, abort
from flask_security import  UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from hashlib import sha256
import os, random, time


def get_data_from_db(table):
    dict = {}
    data = db.session.execute("SELECT * FROM {}".format(table)).cursor.fetchall()
    for i in range(len(data)):
        dict[data[i][0]] = data[i][1]
    return dict

app = Flask(__name__)

app.config["SECRET_KEY"] = "text"
app.config["SECURITY_PASSWORD_SALT"] = "text"
app.config["WTF_CSRF_SECRET_KEY"] = "text"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///static/db/db.app"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_FILE_DIR"] = "./session"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_TYPE"] = "filesystem"

db = SQLAlchemy(app)

#sess = Session(app)

#csrf = CSRFProtect(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30), unique=True)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(512), unique=False)

class Akie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(512), unique=False)

class Connect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(512), unique=False)

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(5), unique=False)


@app.post("/login")
def login():
    session.pop("user_id", None)
    username = str(request.form["key"])
    password = str(request.form["value"])    
    try:
        user = [x for x in User.query.all() if x.username == username and x.password == password][0]
        session["user_id"] = user.id
        #JWT_token = sha256(str(username + "_" + password).encode("UTF-8")).hexdigest()
        print(request.form)
        return "OK"
    except:
        return "ERROR"

@app.get("/admin")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/", methods = ["GET", "POST"])
def user():
    return render_template("user.html")


@app.post("/append_<table>")
def append(table):
    if "user_id" not in session:
        return abort(420)
    db.session.execute("INSERT INTO {} (item) VALUES (\"{}\")".format(table, request.form.get("value")))
    db.session.commit()
    return "True"

@app.post("/delete_<table>")
def delete(table):
    if "user_id" not in session:
        return abort(420)
    db.session.execute("DELETE FROM {} WHERE item = \"{}\"".format(table, request.form.get("value")))
    db.session.commit()
    return "True"

@app.post("/update_<table>")
def update(table):
    if "user_id" not in session:
        return abort(420)
    db.session.execute("UPDATE {} SET item = \"{}\" WHERE id = \"{}\"".format(table, request.form.get("value"), request.form.get("key").replace("item_", "")))
    db.session.commit()
    return "True"

@app.get("/get_data_<table>")
def get_data(table):
    dict = get_data_from_db(str(table))
    return jsonify(dict)

@app.post("/place")
def place():
    if "user_id" not in session:
        print(session)
        return abort(420)
    db.session.execute("UPDATE place SET state = \"{}\" WHERE id = \"{}\"".format(request.form.get("value"), request.form.get("key")))
    db.session.commit()
    return "True"

@app.get("/logout")
def logout():
    if "user_id" in session:
        session.pop("user_id")
    else:
        redirect(url_for(".user"))
    return redirect(url_for(".user"))

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
