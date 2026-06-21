import os
import sqlite3
import json
import database_manager as db


def _init_test_db(db_file: str):
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS Logins(
            Email TEXT PRIMARY KEY NOT NULL,
            passingWord TEXT NOT NULL,
            userID INTEGER UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS servers(
            serverID INTEGER PRIMARY KEY NOT NULL,
            userID INTEGER NOT NULL,
            serverName TEXT NOT NULL,
            sessionsActive INTEGER NOT NULL DEFAULT 0,
            isPrivate INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS serverDetails(
            serverID INTEGER PRIMARY KEY NOT NULL,
            serverPort INTEGER NOT NULL,
            serverHost TEXT NOT NULL,
            secretKey TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS players(
            serverID INTEGER NOT NULL,
            playerName TEXT NOT NULL,
            killCount INTEGER NOT NULL DEFAULT 0,
            deathCount INTEGER NOT NULL DEFAULT 0,
            currentLife INTEGER NOT NULL DEFAULT 3,
            PRIMARY KEY (serverID, playerName)
        );
        """)
    conn.execute(
        "INSERT INTO Logins (Email, passingWord, userID) VALUES (?, ?, ?)",
        ("test@example.com", "hash", 346224),
    )
    conn.execute(
        "INSERT INTO servers (serverID, userID, serverName, isPrivate) VALUES (?, ?, ?, ?)",
        (866784, 346224, "Test Server", 1),
    )
    conn.execute(
        "INSERT INTO serverDetails (serverID, serverPort, serverHost, secretKey) VALUES (?, ?, ?, ?)",
        (866784, 25565, "127.0.0.1", "dummy"),
    )
    conn.commit()
    conn.close()


def _write_log(log_path: str):
    lines = [
        {"ts": "2026-06-20T16:13:19.176826Z", "event": "listener_started"},
        {
            "ts": "2026-06-20T16:29:58.268648Z",
            "event": "join",
            "data": {"type": "join", "player": "sphisi"},
        },
        {
            "ts": "2026-06-20T16:30:26.062764Z",
            "event": "death",
            "data": {"type": "death", "player": "sphisi"},
        },
        {
            "ts": "2026-06-20T16:31:00.000000Z",
            "event": "join",
            "data": {"type": "join", "player": "alex"},
        },
        {
            "ts": "2026-06-20T16:31:20.000000Z",
            "event": "join",
            "data": "bad_data_shape_should_be_ignored",
        },
        {
            "ts": "2026-06-20T16:31:40.000000Z",
            "event": "death",
            "data": {"type": "death", "player": "alex"},
        },
    ]
    with open(log_path, "w", encoding="utf-8") as f:
        for item in lines:
            f.write(json.dumps(item) + "\n")
        f.write("{not-json}\n")  # malformed line should be ignored safely


def test_event_log_create_add_players_update_deaths(tmp_path, monkeypatch):
    base_dir = tmp_path
    (base_dir / "Flaskapp" / "databases").mkdir(parents=True, exist_ok=True)
    (base_dir / "Flaskapp" / "logs").mkdir(parents=True, exist_ok=True)

    db_file = base_dir / "Flaskapp" / "databases" / "servers.db"
    _init_test_db(str(db_file))

    monkeypatch.setattr(db, "_BASE_DIR", str(base_dir))
    monkeypatch.setattr(db, "dbPath", str(db_file))

    ok, log_path = db.create_event_log(866784, 346224)
    assert ok is True
    assert os.path.exists(log_path)

    _write_log(log_path)

    ok_players, msg_players = db.add_players_from_log(866784, 346224)
    assert ok_players is True, msg_players

    ok_deaths, msg_deaths = db.update_player_deaths(866784, 346224)
    assert ok_deaths is True, msg_deaths

    conn = db.dbConnect()
    rows = conn.execute(
        "SELECT playerName, deathCount FROM players WHERE serverID = ? ORDER BY playerName",
        (866784,),
    ).fetchall()
    conn.close()

    assert len(rows) == 2
    assert rows[0]["playerName"] == "alex"
    assert rows[0]["deathCount"] == 1
    assert rows[1]["playerName"] == "sphisi"
    assert rows[1]["deathCount"] == 1
