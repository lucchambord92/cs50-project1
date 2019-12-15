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
        user = db.execute("SELECT name FROM users WHERE id=:id", {"id": user_id}).first()
        name = user.name
    except:
        return render_template("login.html")
    return render_template("login.html", name=name)

@app.route("/login/", methods=["GET", "POST"])
def login():
    error = ""
    try:
        # if user already login, go directly to search page
        user_id = session['user-id']
        user = db.execute("SELECT name FROM users WHERE id=:id", {"id": user_id}).first()
        name = user.name
        return render_template("login.html", name=name)
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
                return render_template("search.html", name=name)
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

@app.route("/search", methods=["GET"])
def search(isbn="", title="", author=""):
    isbn = request.args['isbn']
    title = request.args["title"]
    author = request.args["author"]
    books = []
    if isbn:
        books += db.execute("SELECT * FROM books WHERE isbn LIKE '%' || :isbn || '%'", {"isbn":isbn})
    if title:
        books += db.execute(
            "SELECT * FROM books WHERE title LIKE '%' || :title || '%'", {"title":title}
        )
    if author:
        books += db.execute(
            "SELECT * FROM books WHERE author LIKE '%' || :author || '%'", {"author":author}
        )
    return render_template("books.html", books=books)


    




