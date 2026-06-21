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
from collections import OrderedDict

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


# login required decorator for secure functions
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
                return redirect(url_for("search"))
            else:
                message = "Invalid email or password"

    return render_template("login.html", message=message)


# logout and end session
@app.route("/logout.html", methods=["GET"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@app.route("/search", methods=["GET"])
def search():
    search = request.args.get("search", "").strip()
    results = []
    if search:
        results = dbhandler.search_servers(search)

    leaderboard_groups = dbhandler.get_leaderboard_groups(search)
    return render_template(
        "search.html",
        search=search,
        results=results,
        leaderboard_groups=leaderboard_groups,
    )


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    search = request.args.get("search", "").strip()
    leaderboard_groups = dbhandler.get_leaderboard_groups(search)
    return render_template(
        "leaderboard.html", search=search, leaderboard_groups=leaderboard_groups
    )


# server related methods
@app.route("/myservers.html", methods=["POST", "GET"])
@login_required
def my_servers():
    message = ""
    if request.method == "POST":
        serverID = request.form.get("serverID")
        if serverID:
            success, message = dbhandler.delete_server(int(serverID), session["userID"])

    servers = dbhandler.get_user_servers(session["userID"])
    return render_template("myservers.html", servers=servers, message=message)


@app.route("/serveradd.html", methods=["GET", "POST"])
@login_required
def serveradd():
    message = ""

    if request.method == "POST":
        serverName = request.form.get("serverName", "").strip()
        serverHost = request.form.get("serverHost", "").strip()
        serverPort_raw = request.form.get("serverPort", "").strip()
        serverKey = request.form.get("masterkey", "").strip()
        privacy = request.form.get("privacy", "private")
        isPrivate = 1 if privacy == "private" else 0
        userID = session["userID"]

        if not serverName or not serverHost or not serverPort_raw or not serverKey:
            message = "All fields are required."
            return render_template("serveradd.html", message=message)

        try:
            serverPort = int(serverPort_raw)
            if serverPort < 1 or serverPort > 65535:
                raise ValueError
        except ValueError:
            message = "Port must be a number between 1 and 65535."
            return render_template("serveradd.html", message=message)

        for _ in range(5):
            serverID = random.randint(100000, 999999)
            ok, db_message = dbhandler.add_server_details(
                serverName=serverName,
                userID=userID,
                serverID=serverID,
                serverPort=serverPort,
                serverHost=serverHost,
                serverKey=serverKey,
                isPrivate=isPrivate,
            )
            if ok:
                return render_template("serveradd.html", message=db_message)
            message = db_message

        if not message:
            message = "Could not add server. Try again."

    return render_template("serveradd.html", message=message)


@app.route("/server/edit/<int:serverID>", methods=["GET", "POST"])
@login_required
def edit_server(serverID):
    ok, server, msg = dbhandler.get_server_for_edit(serverID, session["userID"])
    if not ok:
        servers = dbhandler.get_user_servers(session["userID"])
        return render_template("myservers.html", servers=servers, message=msg)

    message = ""
    if request.method == "POST":
        serverName = request.form.get("serverName", "").strip()
        serverHost = request.form.get("serverHost", "").strip()
        serverPort_raw = request.form.get("serverPort", "").strip()
        serverKey = request.form.get("masterkey", "").strip()
        privacy = request.form.get("privacy", "private")
        isPrivate = 1 if privacy == "private" else 0

        if not serverName or not serverHost or not serverPort_raw or not serverKey:
            message = "All fields are required."
            return render_template("edit_server.html", server=server, message=message)

        try:
            serverPort = int(serverPort_raw)
            if serverPort < 1 or serverPort > 65535:
                raise ValueError
        except ValueError:
            message = "Port must be a number between 1 and 65535."
            return render_template("edit_server.html", server=server, message=message)

        success, db_message = dbhandler.update_server_details(
            serverID=serverID,
            userID=session["userID"],
            serverName=serverName,
            serverHost=serverHost,
            serverPort=serverPort,
            serverKey=serverKey,
            isPrivate=isPrivate,
        )
        if success:
            return redirect(url_for("my_servers"))

        message = db_message

    return render_template("edit_server.html", server=server, message=message)


@app.route("/server/start/<int:serverID>", methods=["POST"])
@login_required
def start_server(serverID):
    success, details, msg = dbhandler.get_server_connection_details(
        serverID, session["userID"]
    )

    if not success:
        servers = dbhandler.get_user_servers(session["userID"])
        return render_template("myservers.html", servers=servers, message=msg)

    # ensure event log exists before listener starts writing
    log_ok, log_msg = dbhandler.create_event_log(serverID, session["userID"])
    if not log_ok:
        servers = dbhandler.get_user_servers(session["userID"])
        return render_template("myservers.html", servers=servers, message=log_msg)

    ok, result = mcwebapi.fetch_server_info(
        host=details["serverHost"],
        port=details["serverPort"],
        masterkey=details["serverKey"],
    )

    servers = dbhandler.get_user_servers(session["userID"])
    if not ok:
        return render_template(
            "myservers.html",
            servers=servers,
            message=f"Could not reach server: {result}",
        )

    listener_id = f"{session['userID']}:{serverID}"
    log_file = os.path.join(
        app.root_path, "Flaskapp", "logs", f"events_{session['userID']}_{serverID}.txt"
    )

    started, listener_msg = mcwebapi.start_event_listener(
        listener_id=listener_id,
        host=details["serverHost"],
        port=details["serverPort"],
        masterkey=details["serverKey"],
        output_file=log_file,
    )

    message = ("Server is online! " + listener_msg) if started else listener_msg
    return render_template(
        "myservers.html",
        servers=servers,
        message=message,
        server_info=result,
    )


@app.route("/server/end/<int:serverID>", methods=["POST"])
@login_required
def end_server(serverID):
    userID = session.get("userID")
    if not userID:
        return redirect(url_for("login"))

    listener_id = f"{userID}:{serverID}"
    ok, msg = mcwebapi.stop_event_listener(listener_id)

    servers = dbhandler.get_user_servers(userID)
    return render_template("myservers.html", servers=servers, message=msg)


@app.route("/server/sync_players/<int:serverID>", methods=["POST"])
@login_required
def sync_players(serverID):
    userID = session["userID"]

    ok_last, last_sync_ts, msg_last = dbhandler.get_server_last_sync(serverID, userID)
    if not ok_last:
        servers = dbhandler.get_user_servers(userID)
        return render_template("myservers.html", servers=servers, message=msg_last)

    # single call replaces three separate sync calls
    msg_players, msg_deaths, msg_kills = dbhandler.sync_all_log_events(
        serverID, userID, last_sync_ts
    )

    latest_ts = dbhandler.get_latest_log_ts(serverID, userID)
    if latest_ts and ((not last_sync_ts) or (latest_ts > last_sync_ts)):
        dbhandler.set_server_last_sync(serverID, userID, latest_ts)

    message = f"Players: {msg_players} | Deaths: {msg_deaths} | Kills: {msg_kills}"
    servers = dbhandler.get_user_servers(userID)
    return render_template("myservers.html", servers=servers, message=message)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
