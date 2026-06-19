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
    serverPort: int,
    serverHost: str,
    isPrivate: int = 1,
) -> bool:
    conn = dbConnect()
    try:
        conn.execute(
            "INSERT INTO servers (serverHost, serverPort, userID, serverName, isPrivate) VALUES (?, ?, ?, ?, ?)",
            (serverHost, serverPort, userID, serverName, isPrivate),
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
    conn = dbConnect()
    try:
        pw_hash = bcrypt.hashpw(passingWord.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )
        conn.execute(
            "Insert Into Logins (Email, passingWord, userID) Values(?, ?, ?)",
            (Email.strip().lower(), pw_hash, userID),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        return False
    finally:
        conn.close()


def login_user(Email: str, passingWord: str):
    conn = dbConnect()
    try:
        row = conn.execute(
            "Select passingWord From Logins Where Email = ?",
            (Email.strip().lower(),),
        ).fetchone()
        if not row:
            return False

        return bcrypt.checkpw(
            passingWord.encode("utf-8"),
            row["passingWord"].encode("utf-8"),
        )
    except Exception as e:
        print(f"login error: {e}")
        return False
    finally:
        conn.close()


def check_User(Email: str) -> bool:
    conn = dbConnect()
    row = conn.execute(
        "Select * From Logins Where Email = ?", (Email.strip().lower(),)
    ).fetchone()
    conn.close()
    return row is not None
