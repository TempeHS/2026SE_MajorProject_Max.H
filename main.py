from flask import Flask
from flask import render_template
from flask import request
import database_manager as dbhandler
from flask import session
from flask import redirect
from flask import url_for
import random

app = Flask(
    __name__,
    template_folder="Flaskapp/templates",
    static_folder="Flaskapp/static",
)

# CHANGE DO NOT USE FOR FINAL THINGY
app.config["SECRET_KEY"] = "your_temporary_local_dev_key_here"


@app.route("/")
@app.route("/search", methods=["GET"])
def search():
    search = request.args.get("search", "").strip()
    results = []
    leaderboards = dbhandler.get_leaderboards(search)

    if search:
        results = dbhandler.search_servers(search)
        leaderboards = dbhandler.get_leaderboards(search)

    return render_template(
        "search.html", search=search, results=results, leaderboards=leaderboards
    )


# function for both login and signup
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
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
                message = "Login Succesful"
            else:
                message = "Invalid email or password"

    return render_template("login.html", message=message)


@app.route("/serveradd.html", methods=["POST", "GET"])
def serveradd():
    return render_template("/serverdd.html")


@app.route("/logout.html", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
