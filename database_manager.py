import sqlite3
import bcrypt
import os
from cryptography.fernet import Fernet, InvalidToken
import sqlite3
import bcrypt
import os
import json

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
        # DEV ONLY - remove before production
        key = "KRZmf6DyQNCcLYiNnV2pLXqdBCxdKcYNi6Vn-i_824Q="
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


def get_user_servers(userID: int) -> list:
    conn = dbConnect()
    rows = conn.execute(
        """
        SELECT s.serverID, s.serverName, d.serverHost, d.serverPort
        FROM servers s
        JOIN serverDetails d ON d.serverID = s.serverID
        WHERE s.userID = ?
        """,
        (userID,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_server(serverID: int, userID: int) -> tuple[bool, str]:
    conn = dbConnect()
    try:
        # check the server belongs to the user first
        row = conn.execute(
            "SELECT serverID FROM servers WHERE serverID = ? AND userID = ?",
            (serverID, userID),
        ).fetchone()

        if not row:
            return False, "Server not found or you do not own it."

        conn.execute("DELETE FROM servers WHERE serverID = ?", (serverID,))
        conn.commit()
        return True, "Server deleted."

    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_server_for_edit(serverID: int, userID: int) -> tuple[bool, dict | None, str]:
    conn = dbConnect()
    try:
        row = conn.execute(
            """
            SELECT s.serverID, s.serverName, s.isPrivate, d.serverHost, d.serverPort, d.secretKey
            FROM servers s
            JOIN serverDetails d ON d.serverID = s.serverID
            WHERE s.serverID = ? AND s.userID = ?
            """,
            (serverID, userID),
        ).fetchone()

        if not row:
            return False, None, "Server not found or you do not own it."

        data = dict(row)
        data["serverKey"] = _decrypt(data["secretKey"])
        data.pop("secretKey", None)
        return True, data, ""
    except Exception as e:
        return False, None, str(e)
    finally:
        conn.close()


def update_server_details(
    serverID: int,
    userID: int,
    serverName: str,
    serverHost: str,
    serverPort: int,
    serverKey: str,
    isPrivate: int,
) -> tuple[bool, str]:
    conn = dbConnect()
    try:
        owned = conn.execute(
            "SELECT 1 FROM servers WHERE serverID = ? AND userID = ?",
            (serverID, userID),
        ).fetchone()
        if not owned:
            return False, "Server not found or you do not own it."

        encrypted_key = _encrypt(serverKey)

        conn.execute(
            "UPDATE servers SET serverName = ?, isPrivate = ? WHERE serverID = ?",
            (serverName, isPrivate, serverID),
        )
        conn.execute(
            """
            UPDATE serverDetails
            SET serverHost = ?, serverPort = ?, secretKey = ?
            WHERE serverID = ?
            """,
            (serverHost, serverPort, encrypted_key, serverID),
        )
        conn.commit()
        return True, "Server updated."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


# adds palyers to palyers table
def add_players_from_log(serverID: int, userID: int) -> tuple[bool, str]:
    """Reads the event log for a server and adds any new unique players to the players table."""
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(
        _BASE_DIR, "Flaskapp", "logs", f"events_{userID}_{serverID}.txt"
    )

    if not os.path.exists(log_file):
        return False, "No log file found for this server."

    seen: set[str] = set()

    with open(log_file, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if record.get("event") == "join":
                player = record.get("data", {}).get("player", "").strip()
                if player:
                    seen.add(player)

    if not seen:
        return False, "No join events found in log."

    conn = dbConnect()
    added = 0
    try:
        for player in seen:
            existing = conn.execute(
                "SELECT 1 FROM players WHERE serverID = ? AND playerName = ?",
                (serverID, player),
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO players (serverID, playerName) VALUES (?, ?)",
                    (serverID, player),
                )
                added += 1
        conn.commit()
        return (
            True,
            f"{added} new player(s) added. {len(seen) - added} already existed.",
        )
    except Exception as e:
        conn.rollback()
        return False, f"DB error: {e}"
    finally:
        conn.close()


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
