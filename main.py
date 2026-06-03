from flask import Flask
from flask import render_template
from flask import request
import database_manager as dbhandler

app = Flask(__name__, template_folder="Flaskapp/templates")


@app.route("/")
@app.route("/mainpage")
def mainpage():
    return render_template("mainpage.html")


@app.route("/search", methods=["GET", "POST"])
def search(): ...


@app.route("/leaderboard", methods=["GET", "POST"])
def leaderboard(): ...


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
