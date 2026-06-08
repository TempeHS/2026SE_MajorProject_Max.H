import sqlite3

dbPath = "Flaskapp/databases/servers.db"


def dbConnect():
    conn = sqlite3.connect(dbPath)
    conn.execute("Pragma foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def add_server(serverName: str, serverID: int, isPrivate: int = 1) -> bool:
    try:
        conn = dbConnect()
        conn.execute(
            "INSERT INTO servers (serverID, serverName, isPrivate) VALUES (?, ?, ?)",
            (serverID, serverName, isPrivate),
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
