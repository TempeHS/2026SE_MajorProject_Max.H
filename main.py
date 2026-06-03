from flask import Flask
from flask import render_template
from flask import request
import database_manager as dbhandler

app = Flask(
    __name__,
    template_folder="Flaskapp/templates",
    static_folder="Flaskapp/static",
)


@app.route("/")
@app.route("/mainpage")
def mainpage():
    return render_template("mainpage.html")


@app.route("/search", methods=["GET"])
def search():
    return render_template("search.html")


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    return render_template("leaderboard.html")


@app.route("/navbar", methods=["POST"])
def navbar():
    return render_template("navbar.html")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
