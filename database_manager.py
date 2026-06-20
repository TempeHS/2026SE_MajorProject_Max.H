import sqlite3
import bcrypt
import mcwebapi
import os
from cryptography.fernet import Fernet

dbPath = "Flaskapp/databases/servers.db"


def dbConnect():
    conn = sqlite3.connect(dbPath)
    conn.execute("Pragma foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _get_fernet():
    key = os.environ.get("SERVER_DETAILS_FERNET_KEY", "").strip()
    if not key:
        raise RuntimeError("Missing SERVER_DETAILS_FERNET_KEY environment variable")
    return Fernet(key.encode("utf-8"))


def _encrypt_secret(serverKey: str) -> str:
    f = _get_fernet()
    return f.encrypt(serverKey.encode("utf-8")).decode("utf-8")


def add_server(
    serverName: str,
    userID: int,
    serverID: int,
    isPrivate: int = 1,
) -> bool:
    conn = dbConnect()
    try:
        conn.execute(
            "INSERT INTO servers (serverID, userID, serverName, isPrivate) VALUES ( ?, ?, ?, ?)",
            (serverID, userID, serverName, isPrivate),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        return False
    finally:
        conn.close()


def server_details(
    serverPort: str,
    serverHost: str,
    serverKey: str,
    serverID: int,
):
    conn = dbConnect()
    try:
        conn.execute(
            "Insert Into serverDetails (serverID, serverPort, serverHost, secretKey) Values (?, ?, ?, ?)",
            (serverID, serverPort, serverHost, serverKey),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        return False
    finally:
        conn.close()


# adds palyers to palyers table
def add_player(): ...


# adds players kills in server kills table, need player 1 and 2, weapon used, time/date, serverhost as reference
def add_player_interaction(): ...


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


def get_userID(email: str):
    conn = dbConnect()
    row = conn.execute(
        "Select userID from Logins Where email = ?", (email.strip().lower(),)
    ).fetchone()
    conn.close()
    return row["userID"] if row else None


def check_User(Email: str) -> bool:
    conn = dbConnect()
    row = conn.execute(
        "Select * From Logins Where Email = ?", (Email.strip().lower(),)
    ).fetchone()
    conn.close()
    return row is not None
