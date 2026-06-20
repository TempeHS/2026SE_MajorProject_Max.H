import sqlite3
import bcrypt
import os
from cryptography.fernet import Fernet, InvalidToken

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dbPath = os.path.join(_BASE_DIR, "Flaskapp", "databases", "servers.db")


def dbConnect():
    conn = sqlite3.connect(dbPath)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


# Fernet functions for encryption and secret key
def _get_fernet() -> Fernet:
    key = os.environ.get("SERVER_FERNET_KEY", "").strip()
    if not key:
        raise RuntimeError("Missing SERVER_FERNET_KEY environment variable")
    return Fernet(key.encode("utf-8"))


# encryption using fernet
def _encrypt(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


# decrypt using secret key
def _decrypt(token: str) -> str:
    return _get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")


def add_server_details(
    serverName: str,
    userID: int,
    serverID: int,
    serverPort: int,
    serverHost: str,
    serverKey: str,
    isPrivate: int = 1,
) -> tuple[bool, str]:

    conn = dbConnect()

    try:
        encrypted_key = _encrypt(serverKey)

        conn.execute(
            "INSERT INTO servers (serverID, userID, serverName, isPrivate) VALUES (?, ?, ?, ?)",
            (serverID, userID, serverName, isPrivate),
        )
        conn.execute(
            "INSERT INTO serverDetails (serverID, serverPort, serverHost, secretKey) VALUES (?, ?, ?, ?)",
            (serverID, serverPort, serverHost, encrypted_key),
        )
        conn.commit()
        return True, "Server added successfully."
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, f"Database error: {e}"
    except RuntimeError as e:
        conn.rollback()
        return False, f"Config error: {e}"
    except Exception as e:
        conn.rollback()
        return False, f"Unexpected error: {e}"
    finally:
        conn.close()


# returns server details only for api access to external servers
def get_server_connection_details(
    serverID: int, userID: int
) -> tuple[bool, dict | None, str]:

    conn = dbConnect()
    try:
        row = conn.execute(
            """
            SELECT s.serverID, s.serverName, d.serverHost, d.serverPort, d.secretKey
            FROM servers s
            JOIN serverDetails d ON d.serverID = s.serverID
            WHERE s.serverID = ? AND s.userID = ?
            """,
            (serverID, userID),
        ).fetchone()

        if not row:
            return False, None, "Server not found or access denied."

        return (
            True,
            {
                "serverID": row["serverID"],
                "serverName": row["serverName"],
                "serverHost": row["serverHost"],
                "serverPort": row["serverPort"],
                "serverKey": _decrypt(row["secretKey"]),  # decrypted only in memory
            },
            "ok",
        )

    except InvalidToken:
        return False, None, "Decryption failed: key mismatch."
    except Exception as e:
        return False, None, f"Unexpected error: {e}"
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
