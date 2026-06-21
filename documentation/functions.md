## Database Functions (database_manager.py)

These functions handle all direct interaction with the SQLite database and the event log files.

### Connection & Setup

| Function | Summary |
| --- | --- |
| `dbConnect()` | Opens a connection to `servers.db`, enables foreign keys, sets row factory to dict-style rows, and runs the last-sync column migration before returning the connection. |
| `_ensure_servers_last_sync_column(conn)` | Checks if the `lastSyncTs` column exists on the servers table and adds it if missing. Called automatically inside `dbConnect()`. |

### Encryption

| Function | Summary |
| --- | --- |
| `_get_fernet()` | Reads the Fernet encryption key from the `SERVER_FERNET_KEY` environment variable (falls back to a hardcoded dev key) and returns a `Fernet` instance. |
| `_encrypt(plaintext)` | Encrypts a plaintext string using Fernet and returns the ciphertext. Used to store master keys safely in `serverDetails`. |
| `_decrypt(token)` | Decrypts a Fernet ciphertext token back to plaintext. Called when a master key needs to be passed to `mcwebapi.py` for a curl request. |

### User / Auth

| Function | Summary |
| --- | --- |
| `add_User(Email, passingWord, userID)` | Hashes the password with bcrypt and inserts a new row into the `Logins` table. Returns `True` on success, `False` on duplicate email. |
| `check_User(Email)` | Queries `Logins` for a matching email. Returns `True` if it already exists (used to block duplicate signups). |
| `login_user(Email, passingWord)` | Fetches the stored bcrypt hash for the given email and runs `checkpw` against the supplied password. Returns `True` on a match. |
| `get_userID(email)` | Looks up and returns the `userID` integer for a given email. Called after login to populate the session. |

### Server Management

| Function | Summary |
| --- | --- |
| `add_server_details(...)` | Encrypts the master key, then inserts a row into both `servers` and `serverDetails`. Returns a `(bool, message)` tuple. |
| `get_user_servers(userID)` | Returns a list of all servers owned by the given user, joining `servers` and `serverDetails` for host/port info. Passed to `myservers.html`. |
| `get_server_connection_details(serverID, userID)` | Fetches and decrypts the connection details (host, port, master key) for a specific server. Only succeeds if the server belongs to the user. Passed to `mcwebapi.py`. |
| `get_server_for_edit(serverID, userID)` | Same as above but also returns `serverName` and `isPrivate`. Decrypts the key and strips the raw ciphertext before passing data to `edit_server.html`. |
| `update_server_details(...)` | Verifies ownership, re-encrypts the (possibly changed) master key, and updates both `servers` and `serverDetails` rows. |
| `delete_server(serverID, userID)` | Confirms the server belongs to the user, then deletes the `servers` row (cascades to `serverDetails`, `players`, and `serverKills`). |

### Sync Timestamp

| Function | Summary |
| --- | --- |
| `get_server_last_sync(serverID, userID)` | Reads the `lastSyncTs` value for a server. Used at the start of a sync to know which log entries are new. |
| `set_server_last_sync(serverID, userID, lastSyncTs)` | Updates `lastSyncTs` on the server row after a successful sync, preventing old events from being processed again. |
| `get_latest_log_ts(serverID, userID)` | Scans the event log file and returns the most recent timestamp found. Used to set `lastSyncTs` after sync. |

### Event Log

| Function | Summary |
| --- | --- |
| `create_event_log(serverID, userID)` | Creates the log file and its directory if they don't already exist. Called before starting an event listener. |
| `_event_log_path(serverID, userID)` | Helper that builds the file path for a server's event log (`Flaskapp/logs/events_{userID}_{serverID}.txt`). |

### Log Parsing & Sync

| Function | Summary |
| --- | --- |
| `_parse_log(log_file, last_sync_ts)` | Reads the event log once and returns three things: a set of joined player names, a Counter of death counts per player, and a list of confirmed PvP kills. Skips entries older than `last_sync_ts`. |
| `_ts_diff_seconds(ts_a, ts_b)` | Parses two ISO timestamp strings and returns the difference in seconds. Used by `_parse_log` to match kill and death events within a 2-second window. |
| `sync_all_log_events(serverID, userID, last_sync_ts)` | Calls `_parse_log` once, then uses the results to insert new players, increment death counts, record kills in `serverKills`, increment kill counts, and decrement `currentLife`. Returns three status message strings. |

### Leaderboard & Search

| Function | Summary |
| --- | --- |
| `get_leaderboard_groups(search)` | Queries `serverKills` and `players` for all public servers (optionally filtered by name), groups the results by server, and returns a list of dicts. Passed to `search.html` and `leaderboard.html`. |
| `search_servers(search)` | Returns a list of public servers whose name matches the search term. Passed to `search.html`. |

### Internal Schema Helper

| Function | Summary |
| --- | --- |
| `_players_columns(conn)` | Inspects the `players` table schema at runtime to find the correct column names for player name and death count, since these evolved across sprints. Returns a `(name_col, death_col)` tuple. |

---

## Rendering Functions (main.py)

These are Flask route functions. Each one handles an HTTP request and passes data to a Jinja2 template to render a response.

### Auth Routes

| Function | Route | Summary |
| --- | --- | --- |
| `login()` | `GET/POST /login` | Handles both login and signup in one route. On POST, branches on the `action` field — calls `check_User` / `add_User` for signup, or `login_user` for login. On successful login, sets the session and redirects to `/search`. Renders `login.html`. |
| `logout()` | `GET /logout.html` | Clears the session and redirects to `/login`. Protected by `@login_required`. |

### Search & Leaderboard Routes

| Function | Route | Summary |
| --- | --- | --- |
| `search()` | `GET /` or `GET /search` | Reads the `search` query param, calls `search_servers` and `get_leaderboard_groups`, and renders `search.html` with the results. Accessible without login. |
| `leaderboard()` | `GET /leaderboard` | Calls `get_leaderboard_groups` and renders `leaderboard.html`. Accessible without login. |

### Server Management Routes

| Function | Route | Summary |
| --- | --- | --- |
| `my_servers()` | `GET/POST /myservers.html` | Fetches the user's servers and renders `myservers.html`. On POST, handles a delete request by calling `delete_server` before re-rendering the list. Protected by `@login_required`. |
| `serveradd()` | `GET/POST /serveradd.html` | Validates form input (port range, required fields), then calls `add_server_details` up to 5 times with random IDs until one succeeds. Renders `serveradd.html`. Protected by `@login_required`. |
| `edit_server(serverID)` | `GET/POST /server/edit/<serverID>` | Loads the server via `get_server_for_edit` and renders `edit_server.html`. On POST, validates input and calls `update_server_details`. Redirects to `my_servers` on success. Protected by `@login_required`. |

### Event Listener Routes

| Function | Route | Summary |
| --- | --- | --- |
| `start_server(serverID)` | `POST /server/start/<serverID>` | Gets connection details, ensures the log file exists, verifies the server is reachable via `mcwebapi.fetch_server_info`, then calls `mcwebapi.start_event_listener` to begin streaming events. Re-renders `myservers.html` with a status message. Protected by `@login_required`. |
| `end_server(serverID)` | `POST /server/end/<serverID>` | Calls `mcwebapi.stop_event_listener` to terminate the curl subprocess for this server. Re-renders `myservers.html` with a status message. Protected by `@login_required`. |
| `sync_players(serverID)` | `POST /server/sync_players/<serverID>` | Gets the last sync timestamp, calls `sync_all_log_events` to process new log entries, then updates `lastSyncTs`. Re-renders `myservers.html` with a combined status message. Protected by `@login_required`. |

---

## API / Listener Functions (mcwebapi.py)

These functions communicate with the external Minecraft REST API using curl subprocesses.

| Function | Summary |
| --- | --- |
| `fetch_server_info(host, port, masterkey)` | Sends a GET request to `/api/server` on the Minecraft server using curl. Returns `(True, data_dict)` on success or `(False, error_string)` on failure. Called by `start_server()` to confirm the server is reachable before starting a listener. |
| `start_event_listener(listener_id, host, port, masterkey, output_file)` | Spawns a persistent curl subprocess subscribing to the SSE event stream at `/api/events/stream`. Starts two threads — one to write events to the log file, one to capture curl stderr. Stores the process in `ACTIVE_LISTENERS`. |
| `stop_event_listener(listener_id)` | Looks up the running subprocess in `ACTIVE_LISTENERS`, terminates it (force-kills if it doesn't stop within 3 seconds), and removes it from the dict. |
| `_write_stream_to_file(proc, output_file)` | Runs in a background thread. Reads SSE lines from the curl stdout, assembles them into event records (`ts`, `event`, `data`), and appends each as a JSON line to the log file. |
| `_safe_json(value)` | Attempts to parse a string as JSON. Returns the parsed object on success, or the original string on failure. Used to handle SSE data fields that may or may not be JSON. |

---

## Decorator (main.py)

| Function | Summary |
| --- | --- |
| `login_required(f)` | A route decorator that checks for `'email'` in the session before allowing access. Redirects to `/login` if not present. Wraps any route that requires authentication. |
