import sqlite3
import bcrypt
import os
import json
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from cryptography.fernet import Fernet, InvalidToken

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dbPath = os.path.join(_BASE_DIR, "Flaskapp", "databases", "servers.db")


def _ensure_servers_last_sync_column(conn: sqlite3.Connection) -> None:
    cols = [
        row["name"] for row in conn.execute("PRAGMA table_info(servers)").fetchall()
    ]
    if "lastSyncTs" not in cols:
        conn.execute("ALTER TABLE servers ADD COLUMN lastSyncTs TEXT")
        conn.commit()


def dbConnect():
    conn = sqlite3.connect(dbPath)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    _ensure_servers_last_sync_column(conn)
    return conn


def _get_fernet() -> Fernet:
    key = os.environ.get("SERVER_FERNET_KEY", "").strip()
    if not key:
        # DEV ONLY - remove before production
        key = "KRZmf6DyQNCcLYiNnV2pLXqdBCxdKcYNi6Vn-i_824Q="
    return Fernet(key.encode("utf-8"))


def _encrypt(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def _decrypt(token: str) -> str:
    return _get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")


def _players_columns(conn: sqlite3.Connection) -> tuple[str, str | None]:
    cols = [
        row["name"] for row in conn.execute("PRAGMA table_info(players)").fetchall()
    ]
    name_col = next(
        (c for c in ("playerName", "player", "username") if c in cols), None
    )
    death_col = next(
        (c for c in ("deaths", "deathCount", "playerDeaths") if c in cols), None
    )
    if not name_col:
        raise RuntimeError(
            "players table must contain one of: playerName, player, username"
        )
    return name_col, death_col


def _ts_diff_seconds(ts_a: str, ts_b: str) -> float:
    def _parse(ts: str):
        ts = ts.rstrip("Z").split(".")[0]
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)

    try:
        return (_parse(ts_a) - _parse(ts_b)).total_seconds()
    except Exception:
        return 999.0


def _event_log_path(serverID: int, userID: int) -> str:
    return os.path.join(
        _BASE_DIR, "Flaskapp", "logs", f"events_{userID}_{serverID}.txt"
    )


def _parse_log(
    log_file: str, last_sync_ts: str | None = None
) -> tuple[set[str], Counter, list[dict]]:
    """
    Reads the event log once and returns:
      - joined:  set of player names from join events
      - deaths:  Counter of player name -> death count
      - kills:   list of {killerName, killedName, weaponUsed, timeOfDeath}
    """
    KILL_PHRASES = [
        "was slain by",
        "was shot by",
        "was fireballed by",
        "was killed by",
        "was blown up by",
        "was burnt by",
        "was pummeled by",
        "was impaled by",
        "was stung by",
        "was obliterated by",
    ]

    joined: set[str] = set()
    deaths: Counter = Counter()
    kill_candidates: list[dict] = []
    death_events: list[dict] = []

    with open(log_file, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError:
                continue

            ts = str(record.get("ts", "")).strip()
            if last_sync_ts and ts and ts <= last_sync_ts:
                continue

            event_type = record.get("event", "")
            data = record.get("data", {})
            if not isinstance(data, dict):
                continue

            if event_type == "join":
                player = str(data.get("player", "")).strip()
                if player:
                    joined.add(player)

            elif event_type == "death":
                player = str(data.get("player", "")).strip()
                if player:
                    deaths[player] += 1
                    death_events.append({"ts": ts, "player": player})

            elif event_type == "game":
                content = str(data.get("content", "")).strip()
                for phrase in KILL_PHRASES:
                    if phrase in content:
                        parts = content.split(phrase, 1)
                        killed = parts[0].strip()
                        killer = parts[1].strip() if len(parts) > 1 else ""
                        if killed and killer:
                            kill_candidates.append(
                                {
                                    "ts": ts,
                                    "killedName": killed,
                                    "killerName": killer,
                                }
                            )
                        break

    # pair game kill events with death confirmations within 2 seconds
    kills: list[dict] = []
    used_deaths: set[int] = set()
    for candidate in kill_candidates:
        for i, death in enumerate(death_events):
            if i in used_deaths:
                continue
            if death["player"] != candidate["killedName"]:
                continue
            if death["ts"] < candidate["ts"]:
                continue
            if abs(_ts_diff_seconds(death["ts"], candidate["ts"])) <= 2:
                used_deaths.add(i)
                kills.append(
                    {
                        "killerName": candidate["killerName"],
                        "killedName": candidate["killedName"],
                        "weaponUsed": "fists",
                        "timeOfDeath": death["ts"],
                    }
                )
                break

    return joined, deaths, kills


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


# returns are servers for the logged in user
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


# three functions to ensure that no old logs are added
def get_server_last_sync(serverID: int, userID: int) -> tuple[bool, str | None, str]:
    conn = dbConnect()
    try:
        row = conn.execute(
            "SELECT lastSyncTs FROM servers WHERE serverID = ? AND userID = ?",
            (serverID, userID),
        ).fetchone()
        if not row:
            return False, None, "Server not found or access denied."
        return True, row["lastSyncTs"], "ok"
    except Exception as e:
        return False, None, str(e)
    finally:
        conn.close()


def set_server_last_sync(
    serverID: int, userID: int, lastSyncTs: str
) -> tuple[bool, str]:
    conn = dbConnect()
    try:
        cur = conn.execute(
            "UPDATE servers SET lastSyncTs = ? WHERE serverID = ? AND userID = ?",
            (lastSyncTs, serverID, userID),
        )
        conn.commit()
        if cur.rowcount == 0:
            return False, "Server not found or access denied."
        return True, "lastSyncTs updated."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_latest_log_ts(serverID: int, userID: int) -> str | None:
    log_file = _event_log_path(serverID, userID)
    if not os.path.exists(log_file):
        return None

    latest: str | None = None
    with open(log_file, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError:
                continue
            ts = str(record.get("ts", "")).strip()
            if not ts:
                continue
            if latest is None or ts > latest:
                latest = ts
    return latest


def create_event_log(serverID: int, userID: int) -> tuple[bool, str]:
    log_file = _event_log_path(serverID, userID)
    log_dir = os.path.dirname(log_file)

    try:
        os.makedirs(log_dir, exist_ok=True)
        if not os.path.exists(log_file):
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("")
        return True, log_file
    except Exception as e:
        return False, f"Could not create/open event log: {e}"


# when the sync buttons is pressed all events are then synced with the database
def sync_all_log_events(
    serverID: int, userID: int, last_sync_ts: str | None = None
) -> tuple[str, str, str]:
    log_file = _event_log_path(serverID, userID)
    if not os.path.exists(log_file):
        return "No log file.", "No log file.", "No log file."

    # Parse once for all sync operations
    joined, death_counts, kills = _parse_log(log_file, last_sync_ts)

    conn = dbConnect()
    try:
        name_col, death_col = _players_columns(conn)

        player_cols = [
            row["name"] for row in conn.execute("PRAGMA table_info(players)").fetchall()
        ]
        kill_col = next(
            (c for c in ("killCount", "kills", "playerKills") if c in player_cols), None
        )

        # sync players (join events)
        players_added = 0
        for player in joined:
            exists = conn.execute(
                f"SELECT 1 FROM players WHERE serverID = ? AND {name_col} = ?",
                (serverID, player),
            ).fetchone()
            if not exists:
                conn.execute(
                    f"INSERT INTO players (serverID, {name_col}) VALUES (?, ?)",
                    (serverID, player),
                )
                players_added += 1

        players_msg = (
            f"{players_added} new player(s), {len(joined) - players_added} already existed."
            if joined
            else "No new join events."
        )

        # sync deaths
        deaths_updated = 0
        deaths_inserted = 0
        if death_col:
            for player, count in death_counts.items():
                exists = conn.execute(
                    f"SELECT 1 FROM players WHERE serverID = ? AND {name_col} = ?",
                    (serverID, player),
                ).fetchone()
                if not exists:
                    conn.execute(
                        f"INSERT INTO players (serverID, {name_col}, {death_col}) VALUES (?, ?, ?)",
                        (serverID, player, count),
                    )
                    deaths_inserted += 1
                else:
                    conn.execute(
                        f"UPDATE players SET {death_col} = COALESCE({death_col}, 0) + ? "
                        f"WHERE serverID = ? AND {name_col} = ?",
                        (count, serverID, player),
                    )
                    deaths_updated += 1

        deaths_msg = (
            f"Deaths synced. Updated: {deaths_updated}, inserted: {deaths_inserted}."
            if death_counts
            else "No new death events."
        )

        # sync kills + increment player kill count + lives
        kills_inserted = 0
        player_kills_updated = 0
        player_kills_inserted = 0

        for kill in kills:
            conn.execute(
                """
                INSERT INTO serverKills
                (serverID, playerKillerName, playerKilledName, weaponUsed, timeOfDeath)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    serverID,
                    kill["killerName"],
                    kill["killedName"],
                    kill["weaponUsed"],
                    kill["timeOfDeath"],
                ),
            )
            kills_inserted += 1

            # increment kill count
            if kill_col:
                killer = kill["killerName"]
                exists = conn.execute(
                    f"SELECT 1 FROM players WHERE serverID = ? AND {name_col} = ?",
                    (serverID, killer),
                ).fetchone()
                if not exists:
                    conn.execute(
                        f"INSERT INTO players (serverID, {name_col}, {kill_col}) VALUES (?, ?, ?)",
                        (serverID, killer, 1),
                    )
                    player_kills_inserted += 1
                else:
                    conn.execute(
                        f"UPDATE players SET {kill_col} = COALESCE({kill_col}, 0) + 1 "
                        f"WHERE serverID = ? AND {name_col} = ?",
                        (serverID, killer),
                    )
                    player_kills_updated += 1

                    # palyer life count reduce floor at 0
                    killed = kill["killedName"]
            killed_exists = conn.execute(
                f"SELECT 1 FROM players WHERE serverID = ? AND {name_col} = ?",
                (serverID, killed),
            ).fetchone()
            if not killed_exists:
                # insert with currentLife starting at 2 (already lost 1 life)
                conn.execute(
                    f"INSERT INTO players (serverID, {name_col}, currentLife) VALUES (?, ?, ?)",
                    (serverID, killed, 2),
                )
            else:
                conn.execute(
                    f"""
                    UPDATE players
                    SET currentLife = MAX(0, COALESCE(currentLife, 3) - 1)
                    WHERE serverID = ? AND {name_col} = ?
                    """,
                    (serverID, killed),
                )

        # kill event for serverkills
        if kills:
            if kill_col:
                kills_msg = (
                    f"{kills_inserted} kill(s) recorded. "
                    f"Player kills updated: {player_kills_updated}, inserted: {player_kills_inserted}."
                )
            else:
                kills_msg = (
                    f"{kills_inserted} kill(s) recorded. (No player kill column found)"
                )
        else:
            kills_msg = "No new kill events."

        conn.commit()
        return players_msg, deaths_msg, kills_msg

    except Exception as e:
        conn.rollback()
        err = f"DB error: {e}"
        return err, err, err
    finally:
        conn.close()


# adds a user into the database, called for signup method
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


# logs a user in: used in logni method
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


# gets the specific userID of the logged in user
def get_userID(email: str):
    conn = dbConnect()
    row = conn.execute(
        "Select userID from Logins Where email = ?", (email.strip().lower(),)
    ).fetchone()
    conn.close()
    return row["userID"] if row else None


# checks the email in the logins db
def check_User(Email: str) -> bool:
    conn = dbConnect()
    row = conn.execute(
        "Select * From Logins Where Email = ?", (Email.strip().lower(),)
    ).fetchone()
    conn.close()
    return row is not None


# Returns grouped leaderboard data for all public servers. Each entry: { serverID, serverName, kills: [...] }
def get_leaderboard_groups(search: str = "") -> list[dict]:

    conn = dbConnect()
    try:
        search = (search or "").strip()
        like = f"%{search}%"

        # kills for public servers (optionally filtered by server name)
        kill_query = """
            SELECT s.serverID, s.serverName,
                   sk.playerKillerName, sk.playerKilledName,
                   sk.weaponUsed, sk.timeOfDeath
            FROM serverKills sk
            JOIN servers s ON s.serverID = sk.serverID
            WHERE s.isPrivate = 0
              AND (? = '' OR s.serverName LIKE ?)
            ORDER BY s.serverName ASC, sk.timeOfDeath DESC
        """
        kill_rows = conn.execute(kill_query, (search, like)).fetchall()

        groups: OrderedDict[int, dict] = OrderedDict()
        for row in kill_rows:
            sid = row["serverID"]
            if sid not in groups:
                groups[sid] = {
                    "serverID": sid,
                    "serverName": row["serverName"],
                    "kills": [],
                    "players": [],
                }
            groups[sid]["kills"].append(dict(row))

        # player stats for the same public servers
        players_query = """
            SELECT s.serverID, p.playerName, p.killCount, p.deathCount, p.currentLife
            FROM players p
            JOIN servers s ON s.serverID = p.serverID
            WHERE s.isPrivate = 0
            AND (? = '' OR s.serverName LIKE ?)
            ORDER BY s.serverID, p.playerName
        """
        player_rows = conn.execute(players_query, (search, like)).fetchall()

        for row in player_rows:
            sid = row["serverID"]
            # only attach to servers already shown in leaderboard groups
            if sid in groups:
                groups[sid]["players"].append(
                    {
                        "playerName": row["playerName"],
                        "killCount": row["killCount"],
                        "deathCount": row["deathCount"],
                        "currentLife": row["currentLife"],
                    }
                )

        return list(groups.values())
    finally:
        conn.close()


def search_servers(search: str) -> list[dict]:
    """Returns public servers whose name matches the search term."""
    conn = dbConnect()
    try:
        like = f"%{search.strip()}%"
        rows = conn.execute(
            """
            SELECT s.serverID, s.serverName, d.serverHost, d.serverPort
            FROM servers s
            JOIN serverDetails d ON d.serverID = s.serverID
            WHERE s.isPrivate = 0
            AND s.serverName LIKE ?
            ORDER BY s.serverName ASC
            """,
            (like,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
