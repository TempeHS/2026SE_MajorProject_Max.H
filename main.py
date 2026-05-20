from flask import Flask
from flask import render_template
from flask import request
import database_manager as dbhandler

app = Flask(__name__)


@app.route("/")


@app.route("/index")
def index(): ...


@app.route("/search", methods=["GET", "POST"])