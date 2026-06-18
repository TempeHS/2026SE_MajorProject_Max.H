import sqlite3
import bcrypt

dbPath = "Flaskapp/databases/servers.db"


def dbConnect():
    conn = sqlite3.connect(dbPath)
    conn.execute("Pragma foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def add_server(
    serverName: str,
    userID: int,
    serverID: int,
    isPrivate: int = 1,
) -> bool:
    try:
        conn = dbConnect()
        conn.execute(
            "INSERT INTO servers (serverID, userID, serverName, isPrivate) VALUES (?, ?, ?, ?)",
            (serverID, userID, serverName, isPrivate),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        return False
    finally:
        conn.close()


def search_servers(search: str):
    # todo
    return []


def get_leaderboards(search: str):
    conn = dbConnect()
    rows = conn.execute(
        "SELECT serverName AS name, sessionsActive AS score FROM servers ORDER BY sessionsActive DESC"
    ).fetchall()
    conn.close()
    return rows


def add_User(Email: str, passingWord: str, userID: int) -> bool:
    try:
        conn = dbConnect()
        conn.execute(
            "Insert Into Logins (Email, passingWord, userID) Values(?, ?, ?)",
            (Email, passingWord, userID),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        return False
    finally:
        conn.close()


def login_user(Email: str, passingWord: str):
    try:
        conn = dbConnect()
        user = conn.execute(
            "Select * From Logins Where Email = ? and passingWord = ?",
            (Email, passingWord),
        ).fetchone()
        conn.close()
        return user is not None
    except sqlite3.IntegrityError as e:
        print(f"login error: {e}")
        return False
    finally:
        conn.close()


def check_User(Email: str) -> bool:
    conn = dbConnect()
    row = conn.execute("Select * From Logins Where Email = ?", (Email,)).fetchone()
    conn.close()
    return row is not None
