from flask import Flask
from flask import render_template
from flask import request
import database_manager as dbhandler
from flask import session
from flask import redirect
from flask import url_for

app = Flask(
    __name__,
    template_folder="Flaskapp/templates",
    static_folder="Flaskapp/static",
)


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        userID = ""
        action = request.form.get("action", "login")

        # if there is no values in either box
        if not email or not password:
            message = "Please input a email and password"

        # if the user clicks signup
        elif action == "signup":
            # if the email is in the db then return message
            if not dbhandler.check_User(email):
                message = "email already used"
                return message
            # if the email is not the db then return message and add email and password
            elif dbhandler.check_User(email, password, userID):
                dbhandler.add_User(email, password, userID)

            else:
                message = "integrity error"
                return message

        elif action == "login":
            ...


@app.route("/logout.html", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
