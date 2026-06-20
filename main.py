from flask import Flask
from flask import render_template
from flask import request
import database_manager as dbhandler
from flask import session
from flask import redirect
from flask import url_for
import random
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import mcwebapi
import os
from cryptography.fernet import Fernet, InvalidToken

app = Flask(
    __name__,
    template_folder="Flaskapp/templates",
    static_folder="Flaskapp/static",
)

# flask config
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 10800
# CHANGE DO NOT USE FOR FINAL THINGY
app.config["SECRET_KEY"] = "your_temporary_local_dev_key_here"

# add csrf protection
csrf = CSRFProtect(app)


@app.route("/")
@app.route("/search", methods=["GET"])
def search():
    search = request.args.get("search", "").strip()
    results = []
    leaderboards = dbhandler.get_leaderboards(search)

    if search:
        results = dbhandler.search_servers(search)

    return render_template(
        "search.html", search=search, results=results, leaderboards=leaderboards
    )


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


# function for both login and signup
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        action = request.form.get("action", "login")

        # if there is no values in either box
        if not email or not password:
            message = "Please input an email and password"

        # if the user clicks signup
        elif action == "signup":
            # if the email is in the db then return message
            if dbhandler.check_User(email):
                message = "email already used"
            # if the email is not in the db then return message and add email and password
            else:
                added = False
                for i in range(5):
                    userID = random.randint(100000, 999999)
                    if dbhandler.add_User(email, password, userID):
                        added = True
                        break
                message = (
                    "Account created" if added else "Signup Failed, try again shortly"
                )

        elif action == "login":
            if dbhandler.login_user(email, password):
                session["email"] = email
                session["userID"] = dbhandler.get_userID(email)
                message = "Login Succesful"
                redirect(url_for("search"))
            else:
                message = "Invalid email or password"

    return render_template("login.html", message=message)


@app.route("/myservers.html", methods=["POST", "GET"])
@login_required
def my_servers(): ...


@app.route("/serveradd.html", methods=["GET", "POST"])
@login_required
def serveradd():
    if request.method == "POST":
        serverName = request.form.get("servername", "")
        serverHost = request.form.get("serverHost", "")
        serverPort = request.form.get("serverPort", "")
        serverKey = request.form.get("masterKey", "")
        privacy = request.form.get("privacy", "private")
        isPrivate = 1 if privacy == "private" else 0
        userID = session["userID"]
        serverID = int

        for i in range(5):
            serverID = random.randint(100000, 999999)

        return redirect(url_for("my_servers"))

    return render_template("serveradd.html")


@app.route("/logout.html", methods=["GET"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
