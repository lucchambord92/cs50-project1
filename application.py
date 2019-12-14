import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    try:
        user_id = session['user-id']
    except:
        return render_template("login.html")
    return f"user id: {user_id}"

@app.route("/login/", methods=["GET", "POST"])
def login():
    error = ""
    try:
        user_id = session['user-id']
        user = db.execute("SELECT name FROM users WHERE id=:id", {"id": user_id}).first()
        message = f"You are already login as {user.name}"
        return render_template("success.html", message=message)
    except:
        if request.method == "POST":
            name = request.form.get("name")
            password = request.form.get("password")
            user = db.execute("SELECT * FROM users \
                        WHERE name = :name AND password = :password", \
                        {"name":name, "password":password}).first()
            if user is None:
                error = "Incorrect login informations, please try again"
            else:
                session['user-id'] = user.id
                message = f"You are successfully login as {user.name}"
                return render_template("success.html", message=message)
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    try:
        del session['user-id']
        error = "You are successfully logout."
    except:
        error = "You were not login."
    return render_template("login.html", error=error)

@app.route("/registrate", methods=["GET", "POST"])
def registrate():
    error = ""
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        try:
            db.execute("INSERT INTO users (name, password) \
                    VALUES (:name, :password)", \
                    {"name": name, "password": password})
            db.commit()
            return render_template("login.html", error="successfully registrated!")
        except:
            error = "registration impossible, please try with other name."
    return render_template("registrate.html", error=error)




    




