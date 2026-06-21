## Vision

A Webapp designed for the False life / life series community, server owners can connect up their minecraft server and have a leaderboard which can show thier players, kills, deaths, current life count, and player vs palyer interactions, all without having to upload it manually.

## Product Backlog Table

| PB ID | User Story | Priority | Acceptance Criteria | Status |
|---|---|---|---|---|
| PB-01 | User wants to be able to sign up for an account so they can register and manage their own servers | P1 | New account is created with a hashed password and unique userID stored in the Logins table | Done |
| PB-02 | User wants to be able to log in so they can access their servers and management tools | P1 | Valid credentials create an active session and redirect to the search page | Done |
| PB-03 | User wants to be able to log out so their account is secured when they are done | P1 | Session is cleared and user is redirected to the login page | Done |
| PB-04 | User wants to be able to add a Minecraft server so they can start tracking its statistics | P1 | Server details are validated, master key is encrypted, and rows are inserted into both the servers and serverDetails tables | Done |
| PB-05 | User wants to be able to view all their registered servers in one place | P1 | All servers owned by the logged-in user are fetched and rendered correctly on the My Servers page | Done |
| PB-06 | User wants to be able to edit their server's details so they can keep connection information up to date | P1 | Server name, host, port, master key, and privacy setting are updated in the database and only accessible to the server owner | Done |
| PB-07 | User wants to be able to delete a server they own so they can remove it when no longer needed | P1 | Server row is removed from the database and all associated player and kill data is cascade deleted | Done |
| PB-08 | User wants to be able to set their server to public or private so they can control who sees the statistics | P1 | isPrivate flag defaults to private on creation and can be toggled by the owner; private servers do not appear on any public page | Done |
| PB-09 | User wants to be able to start an event listener on their server so statistics are recorded during a live session | P1 | A curl SSE subprocess is spawned and begins writing events to the server's log file; confirmation message is shown to the user | Done |
| PB-10 | User wants to be able to end the event listener when the session is over | P1 | The curl subprocess is terminated and removed from the active listeners dictionary | Done |
| PB-11 | User wants to be able to sync their server so the latest kills, deaths, and player joins are saved to the database | P1 | Log file is parsed, new players are inserted, death and kill counts are updated, and the last sync timestamp is saved to prevent duplicate processing | Done |
| PB-12 | User wants player kill counts to be tracked so they can see who has the most kills | P1 | Kill events from the log are correctly matched using the 2-second pairing window and killCount is incremented for the correct player | Done |
| PB-13 | User wants player death counts to be tracked so they can see how many times each player has died | P1 | Death events are parsed from the log and deathCount is correctly incremented per player in the database | Done |
| PB-14 | User wants player life counts to be tracked so the server group can follow the Life Series format | P1 | currentLife is decremented correctly on each confirmed death and never drops below zero | Done |
| PB-15 | User wants to be able to search for public servers so they can find and view other groups' statistics | P2 | Search query filters public servers by name and returns matching results on the search page | Done |
| PB-16 | User wants to be able to view a public leaderboard so they can see player statistics across servers | P2 | Leaderboard page correctly aggregates and displays kill counts, death counts, and life counts for all public servers | Done |
| PB-17 | User wants server master keys to be stored securely so sensitive credentials are not exposed in a breach | P1 | Master keys are Fernet-encrypted before database insertion and only decrypted in memory when needed for a request | Done |
| PB-18 | User wants the application to be protected against CSRF attacks so malicious forms cannot trigger actions on their behalf | P2 | All POST routes require a valid CSRF token via flask-wtf; requests without one are rejected | Done |
| PB-19 | User wants sessions to expire automatically so their account is not left open indefinitely | P2 | Sessions expire after 3 hours and cookies are set with HTTPONLY to prevent JavaScript access | Done |
| PB-20 | User wants the application to be easy to navigate so non-technical players in the group can use it without help | P2 | All key pages are reachable from the navbar, all actions return clear feedback messages, and no raw errors are shown to the user | Done |
| PB-21 | User wants the leaderboard to only show public servers so private group data is not visible to strangers | P1 | All leaderboard and search queries filter by WHERE isPrivate = 0 at the database level | Done |
| PB-22 | User wants the application to work on mobile so they can check statistics between sessions on their phone | P3 | All pages render correctly on mobile screen sizes using responsive CSS | Done |
| PB-23 | User wants kill feed details recorded per server so the group can see who killed who and with what | P2 | Each confirmed PvP kill is inserted into the serverKills table with killer name, killed name, weapon used, and timestamp | Done |
| PB-24 | User wants the ability to track assists and alliances so the group can manage in-game relationships | P4 | Assist events are detected and stored; alliance/enemy relationships can be set per player pair | Planned |

## Changelog


## 18/05/2026

* Initialised repository and created initial project structure.
* Updated README.md with project overview.

---

## 20/05/2026

* Filled in missing folder structures.
* Relearnt Flask fundamentals and created initial planning documents (`plans`).

---

## 03/06/2026

* **Sprint 1 (Database) started.**
* Created database framework for players and servers.
  * Each server row can have multiple players associated via a foreign key.
* Merged `sprint--database` branch into main.

---

## 08/06/2026

* **Sprint 2 (UI) started.**
* Built workable UI, changed approach to single page with partials.
  * Placeholder server list working — renders data pulled from the database.
* Added new base template and resolved minor structural issues.
* Started investigating the Minecraft-end plugin (MCRESTAPI).
  * Successfully got it to curl from its VM to the host machine.
* Merged `sprint--ui` branch into main.

---

## 10/06/2026

* **Sprint 3 (Connections) started.**
* Worked on SQL database structure, fixed foreign key alignment errors across multiple attempts.

---

## 11/06/2026

* Fixed SQL database issues so multiple players with the same name can exist across different servers.
* Changed reference order so servers are now dependent on logins, and both `serverKills` and `players` are dependent on servers.
* Added HTML pages corresponding to new table structure.
* Pulled across useful boilerplate from another repository.
* Merged `sprint--connection` branch into main.

---

## 16/06/2026

* **Sprint 4 (Frontend) started.**
* Worked on login and signup routes and database handling.
* Authentication, login, and signup flows partially implemented — needed finishing.

---

## 18/06/2026

* Filled out login and signup code so both now work end to end.
* Identified that bcrypt hashing still needed to be added to passwords.
* Noted that `SECRET_KEY` is currently hardcoded — flagged for future fix.
* Fixed minor bugs across routes and templates.

---

## 19/06/2026

* **Sprint 5 (Server Add) started.**
* Fixed most remaining bugs; set up database to correctly handle server IPs and ports.
* Added bcrypt hashing for passwords.
* Added security fixes including session checks and route protection.
* Started building the webapp → Minecraft server connection layer.
* Added further database manager functions in preparation for server adding and curling.

---

## 20/06/2026

* **Sprint 6 (Server Listen) started.**
* Started adding proper server adding functionality with Fernet encryption for master keys.
  * Master key now gets correctly encrypted on server addition.
* Worked on curl requests to the MCRESTAPI — Fernet encryption confirmed operational.
* Server adding fully working; identified port forwarding issue with IP (resolved in next commit).
* Server can now correctly listen on ports, start an event listener, and record new players to the database.
* Merged `sprint--serveradd` branch into main.

---

## 21/06/2026

* Completed major application design — webapp now fully functional end to end:
  * Accepts user IP, port, and master key for server registration.
  * Can start an event listener for a specific server, sending a TCP request before either timing out with an error or beginning to listen.
  * Successfully receives JSON events and appends them to a unique event log per server.
  * Reads log using a timestamp to ensure no old data is re-added on sync.
  * Leaderboard only shows public servers; privacy can be toggled by the server owner at any time.
  * Leaderboard correctly displays player statistics and server statistics.
* Removed redundant code and functions from `database_manager.py`.
* Uploaded sprint summaries to documentation folder.
* Added unit tests across sprints.
* Created `requirements.md`.
* Converted relevant `.txt` files to `.md`.
* Added required documentation structure to repository.
* Merged `sprint--serverlisten` branch into main.
