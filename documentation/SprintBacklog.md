# Sprint-1-database

## Sprint Goal:
* Add basic files structure, add preliminary tables based on data dictionaries and suspected values


## Committed Items:
| Backlog ID | User Request |
| --- | --- |
| PB-04 | User wants to be able to add a Minecraft server so they can start tracking its statistics |
| PB-05 | User wants to be able to view all their registered servers in one place |
| PB-12 | User wants player kill counts to be tracked so they can see who has the most kills |
| PB-13 | User wants player death counts to be tracked so they can see how many times each player has died |
| PB-14 | User wants player life counts to be tracked so the server group can follow the Life Series format |
| PB-23 | User wants kill feed details recorded per server so the group can see who killed who and with what |


## Sprint Plan:
* fill out suspected html skeleton
* add log manager basic routes
* add main.py basic routes
* fill out initial documentation, gantt chart, product ideation


## Unit Tests:
NA


## Client Feedback Summary:
* theres not much to comment on - database setup looks good, - still holding discussion about what the final product should look like

## Response:
* more discussion with clients about what the final product should do


## Sprint Summary/Review:
* added database/table structure
* added basic routes to main.py and logmanager

sprint 1 goals mostly achieved, basic html routes in main.py and their respective html pages are added, mostly just as decorations with no functionality


## Issues and Difficulties:
* ive completely forgotten how to write html code so I have to relearn how to do that


## Evidence:


## Sprint Retrospective:
* use time better
* better planning will enable better workflow
* add in more necessary html pages
* fix any errors that may arise

_________________________________________________________________________________________________________________________

# Sprint-2-ui

## Sprint Goal:
* add frontend webpages workflow, along with their respective routes and any logmanager methods


## Committed Items:
| Backlog ID | User Request |
| --- | --- |
| PB-15 | User wants to be able to search for public servers so they can find and view other groups' statistics |
| PB-16 | User wants to be able to view a public leaderboard so they can see player statistics across servers |
| PB-20 | User wants the application to be easy to navigate so non-technical players in the group can use it without help |
| PB-22 | User wants the application to work on mobile so they can check statistics between sessions on their phone |


## Sprint Plan:
* Create the suspected frontend html files
* fill main.py with html routes
* fix any errors in database
* fill out html with example pages to visualise product
* add example server to database and render to visual product


## Unit Tests:
NA


## Client Feedback Summary:
* webpages are easy to navigate, placeholder serverlist needs to have different data sets in final implementation, being able to signup might be useful

## Response:
* next sprint will include a login, signup feature as well as improving the sqlite3 schema


## Sprint Summary/Review:
* added and changed html layout, added base, navbar, search, leaderboard, mainpage(redundant)

sprint 2 goals achieved to basic functionality, probably shouldve filled out more of it, but am unsure of what maybe required in the future


## Issues and Difficulties:
* Still having trouble remembering how to write html code, started using previous projects as examples


## Evidence:


## Sprint Retrospective:
* better plans means better workflow
* add in proper server add feature in next sprint
* fix any errors that may arise

_________________________________________________________________________________________________________________________

# Sprint-3-connections

## Sprint Goal:
* connect database up to frontend, add basic security features for login and signup


## Committed Items:
| Backlog ID | User Request |
| --- | --- |
| PB-01 | User wants to be able to sign up for an account so they can register and manage their own servers |
| PB-21 | User wants the leaderboard to only show public servers so private group data is not visible to strangers |


## Sprint Plan:
* add functionality for adding a server
* fix database schema to using cascading tables - based on data dictionaries and unit tests
* add stub routes for login and server addition routes and htmls


## Unit Tests:
| Test ID | Test Name | What It Tests | Input | Expected Output | Actual Output | Pass / Fail |
| --- | --- | --- | --- | --- | --- | --- |
| T3-01 | Valid User Signup | `check_User` / `add_User` — new account creation with unique email | New unique email + any password | Returns False from `check_User`; `add_User` inserts row and returns True | `check_User` returns False; `add_User` inserts hashed password and returns True | Pass |
| T3-02 | Duplicate Email Rejection | `check_User` — duplicate email guard before signup | Email already present in Logins table | `check_User` returns True; signup branch shows "email already used" and makes no insert | `check_User` returns True; duplicate insert is blocked and message is displayed | Pass |


## Client Feedback Summary:
* the frontpage is only rendering part of the data needed, even if it is a placeholder, probably add a way to add your own servers

## Response:
* that will happen later


## Sprint Summary/Review:
* fixed sqlite3 table schema, and added more tables
* fixed html referencing, added more functionality to base page, navbar and leaderboard
* added/fixed routes in main and log manager

sprint 3 goals fully achieved, database schema and frontend connectivity work to a basic degree, security features are simple and safe


## Issues and Difficulties:
* sqlite3 code schema is becoming tougher to visualise
* data dictionaries are now out of date


## Evidence:


## Sprint Retrospective:
* the good
  * security features added means user data is safer in case of data breach
* the bad
  * still very little actual functionality
* the future
  * add more complete additions rather than just empty decorations that can be fixed later

_________________________________________________________________________________________________________________________

# Sprint-4-frontend

## Sprint Goal:
* initially fix any errors that may have arisen from the previous sprints, complete login/signup methods and pages with secure hashing and user checks, also add decorator functions for more security


## Committed Items:
| Backlog ID | User Request |
| --- | --- |
| PB-02 | User wants to be able to log in so they can access their servers and management tools |
| PB-03 | User wants to be able to log out so their account is secured when they are done |
| PB-17 | User wants server master keys to be stored securely so sensitive credentials are not exposed in a breach |
| PB-18 | User wants the application to be protected against CSRF attacks so malicious forms cannot trigger actions on their behalf |
| PB-19 | User wants sessions to expire automatically so their account is not left open indefinitely |


## Sprint Plan:
* fix any obvious issues
* add secure hashing to logins/signup route


## Unit Tests:
| Test ID | Test Name | What It Tests | Input | Expected Output | Actual Output | Pass / Fail |
| --- | --- | --- | --- | --- | --- | --- |
| T4-01 | Valid Login | `login_user` — bcrypt password verification on correct credentials | Registered email + correct plaintext password | `login_user` returns True; session stores email and userID | bcrypt.checkpw passes; session is populated and user is redirected to /search | Pass |
| T4-02 | Invalid Password Rejected | `login_user` — bcrypt rejects wrong password for existing email | Registered email + incorrect password | `login_user` returns False; "Invalid email or password" message shown; no session set | bcrypt.checkpw fails; function returns False; no session created | Pass |
| T4-03 | Unauthenticated Route Redirect | `login_required` decorator — blocks access to protected routes without a session | GET /myservers.html with no active session | Request is redirected to /login | Decorator detects missing 'email' key in session and redirects to login | Pass |


## Client Feedback Summary:
* login and signup work, i can log in and see the main page (base, navbar, search) and logout, sqlite3 table looks a lot better filled out, please add functionality to add a server next

## Response:
* next step is to be able to have users add their own servers and render the details


## Sprint Summary:
* added login page and html page
* increased security on login and signup
* added decorator and login/session checks so only some pages are available

sprint 4 goals mostly achieved, errors are fixed, and frontend flow works and can be used


## Issues and Difficulties:
* at this point the log manager was becoming more filled up and the code itself was becoming more complex

## Evidence:


## Sprint Retrospective:
* the good
  * login and signup work complete with secure architecture
* the bad
  * functionality of pieces is still missing
* the future
  * add more complete additions rather than just empty decorations that can be fixed later

_________________________________________________________________________________________________________________________

# Sprint-5-serveradd

## Sprint Goal:
* initially fix any issues from previous sprint, need to add the ability for users to add their own servers making sure to properly encrypt any key information such as master key, current sqlite schema cannot handle server details so that needs to be fixed, also need to clean up html schema and add main and log manager functions to pass the data
* sub goal, attempt to curl an active minecraft server from github codespace/container


## Committed Items:
| Backlog ID | User Request |
| --- | --- |
| PB-04 | User wants to be able to add a Minecraft server so they can start tracking its statistics |
| PB-05 | User wants to be able to view all their registered servers in one place |
| PB-06 | User wants to be able to edit their server's details so they can keep connection information up to date |
| PB-07 | User wants to be able to delete a server they own so they can remove it when no longer needed |
| PB-08 | User wants to be able to set their server to public or private so they can control who sees the statistics |
| PB-17 | User wants server master keys to be stored securely so sensitive credentials are not exposed in a breach |


## Sprint Plan:
* fix previous issues
* add server adding html, server list for users
* fix search, and navbar htmls to work with new schema
* add mcwebapi with basic functionality to see if server is curlable
* fix/add sqlite tables to handle new data types and more information + cascading table schema
* attempt to work out how to curl active minecraft server


## Unit Tests:
| Test ID | Test Name | What It Tests | Input | Expected Output | Actual Output | Pass / Fail |
| --- | --- | --- | --- | --- | --- | --- |
| T5-01 | Server Addition — Valid Input | `add_server_details` — inserts server and encrypts master key at rest | Valid serverName, host, port (25565), masterkey, userID; isPrivate = 1 | Returns (True, "Server added successfully."); serverDetails.secretKey stored as Fernet token, not plaintext | Row inserted in servers and serverDetails; secretKey is encrypted ciphertext | Pass |
| T5-02 | Server Addition — Invalid Port | `main.py` serveradd route — port boundary validation before DB insert | serverPort = 0 (out of range) | "Port must be a number between 1 and 65535." displayed; no DB insert | ValueError raised by int conversion check; error message rendered; no insert attempted | Pass |
| T5-03 | Master Key Decrypt Round-Trip | `_encrypt` / `_decrypt` — Fernet encrypt then decrypt returns original value | Plaintext string 'test-master-key-abc123' | `_decrypt(_encrypt(value))` == original value | Fernet token successfully decrypted back to original plaintext | Pass |


## Client Feedback Summary:
* the frontend still isn't rendering all the details properly, but the addition of being able to add servers is good, might want to be able to edit them though

## Response:
* in the next sprint I will add an editing feature, as well as properly show all the details which we have discussed needs to be shown


## Sprint Summary:
* fixed previous issues
* added server adding functionality when logged in
* figured out how to curl a server from terminal using port, ip and master key
* added my servers html as a decoration, no functionality
* added mcwebapi which should work now that curling has been fixed
* added encryption and decryption methods to log manager
* added functional server add method to main

sprint 5 goal fully achieved, sqlite3 tables now have proper schema, curling requests from github were tested and completed


## Issues and Difficulties:
* imported library methods are becoming very confusing as there is so much inter-communication between built functions and imported ones

## Evidence:


## Sprint Retrospective:
* the good
  * server addition works
  * api is mostly built
  * curling was tested and fixed
  * safer encryption of specific data
* the bad
  * still needs certain parts
  * stop wasting time
* the future
  * add more complete additions rather than just empty decorations that can be fixed later

_________________________________________________________________________________________________________________________

# Sprint-6-serverlisten

## Sprint Goal:
* to finish the event listener, so that players can add a server, start the event listener, webapi will take all relevant events and add them or tally them to the database, then users can end the event listener and view the server, serverkills and player statistics


## Committed Items:
| Backlog ID | User Request |
| --- | --- |
| PB-09 | User wants to be able to start an event listener on their server so statistics are recorded during a live session |
| PB-10 | User wants to be able to end the event listener when the session is over |
| PB-11 | User wants to be able to sync their server so the latest kills, deaths, and player joins are saved to the database |
| PB-12 | User wants player kill counts to be tracked so they can see who has the most kills |
| PB-13 | User wants player death counts to be tracked so they can see how many times each player has died |
| PB-14 | User wants player life counts to be tracked so the server group can follow the Life Series format |
| PB-15 | User wants to be able to search for public servers so they can find and view other groups' statistics |
| PB-16 | User wants to be able to view a public leaderboard so they can see player statistics across servers |
| PB-21 | User wants the leaderboard to only show public servers so private group data is not visible to strangers |
| PB-23 | User wants kill feed details recorded per server so the group can see who killed who and with what |


## Sprint Plan:
* fix any previous issues
* add all event listener types and their respective methods and functions
* simplify functions into smaller functions inside log manager
* fix the displaying of data
* ensure curl works with other servers
* run general limit tests
* stop the pain


## Unit Tests:
| Test ID | Test Name | What It Tests | Input | Expected Output | Actual Output | Pass / Fail |
| --- | --- | --- | --- | --- | --- | --- |
| T6-01 | Ownership Check on Delete | `delete_server` — prevents a user deleting another user's server | serverID belonging to userID 111111; delete attempted by userID 222222 | Returns (False, "Server not found or you do not own it."); row not deleted | Ownership SELECT returns no row; function returns failure tuple; DELETE not executed | Pass |
| T6-02 | Player Sync from Join Events | `sync_all_log_events` — join events add new players; existing players not duplicated | Log with two join events for 'sphisi' and 'alex'; both absent from players table | Two rows inserted in players; players_msg reports "2 new player(s)" | Both players inserted; duplicate join for same player skipped on subsequent sync | Pass |
| T6-03 | Death Counter Increment | `sync_all_log_events` — death events increment deathCount for existing player | Player 'sphisi' already in players table (deathCount = 0); log contains one death event for 'sphisi' | deathCount for 'sphisi' updated to 1 | UPDATE with COALESCE increments deathCount from 0 to 1 | Pass |
| T6-04 | Kill–Death Pairing Within 2 s | `_parse_log` — game event + death event within 2 seconds are matched as a PvP kill | game event 'sphisi was slain by alex' at T+0.0 s; death event for 'sphisi' at T+1.5 s | kills list contains one entry: killerName='alex', killedName='sphisi' | `_ts_diff_seconds` within threshold; kill candidate paired with death confirmation | Pass |
| T6-05 | Kill–Death Pairing Exceeds 2 s | `_parse_log` — game and death events more than 2 seconds apart are NOT matched | game event at T+0.0 s; death event for same player at T+3.0 s | kills list is empty; no spurious kill recorded | `_ts_diff_seconds` = 3.0 > threshold; candidate discarded | Pass |
| T6-06 | Last-Sync Timestamp Filters Old Events | `sync_all_log_events` — events timestamped before lastSyncTs are ignored on re-sync | Log with one join event at T1; lastSyncTs set to T1; sync called again | No new players inserted; msg reports "No new join events." | `_parse_log` skips entries where ts <= last_sync_ts; no duplicate insert | Pass |
| T6-07 | Malformed Log Lines Ignored | `_parse_log` — invalid JSON lines in event log do not raise exceptions | Log file containing `{not-json}` on one line alongside valid records | json.JSONDecodeError caught; malformed line skipped; valid records still processed | try/except around json.loads continues to next line without crash | Pass |
| T6-08 | Leaderboard Shows Only Public Servers | `get_leaderboard_groups` — isPrivate = 1 servers excluded from public leaderboard | Two servers in DB: one public (isPrivate=0), one private (isPrivate=1); both have kill records | `get_leaderboard_groups` returns only the public server's kill data | SQL WHERE isPrivate = 0 filters out private server; only public kills returned | Pass |


## Client Feedback Summary:
* login and sign up work well enough, still might want to add some restrictions on it, it displays all of the necessary data, though functionality for private servers could be good for a future update, searching through servers works, yeah everything works well enough

## Response:
* great


## Sprint Summary:
* fixed any previous issues
* added minor testing file (curl command)
* fixed mcwebapi functionality, curl commands now get properly built inside log manager and passed to mcwebapi which now can connect to my testing mc server (port wasn't forwarded)
* added logging functionality for player kills, player deaths, player life count, players unique to server, player vs player interactions unique to server
* added last sync time so old data wouldn't get added twice on sync
* combined all sync functions so now every event is checked and added at once
* fixed up routes for editing servers
* added necessary functions in log manager
* fixed rendering of servers, now renders server | server players | serverkills

sprint 6 goals fully achieved, website is completely functional, so long as user sets up port forwarding correctly, it just works now with very few visible issues


## Issues and Difficulties:
* main issues are that the log manager was becoming bloated with functions, so had to merge a couple of them together and simplify various ones
* had an issue where server statistics would render twice for a while because of a build-up of different html extend blocks across the different html pages
* curl wasn't that hard yay

## Evidence:


## Sprint Retrospective:
* the good
  * website works completely
  * many edge cases can be caught
  * database is secure on multiple levels
  * can render servers
  * completely user friendly
* the bad
  * still a bit ugly looking
* the future

_________________________________________________________________________________________________________________________

# Future Additions and Product Deployment Specifications

## Future Additions
Future additions would include a nicer looking UI, stricter password and email requirements, better handling of edge cases, a wider array of event type listeners so more data can be displayed.

## Product Deployment

### Issues

Currently the Fernet encryption seed is hardcoded in. This key encrypts the masterkey used to send curl requests to the MCREST API. It is currently hardcoded as having it in the env variable would delete the key on startup and thus the master key wouldn't get properly decrypted and the curl requests would fail.
If the product were to be fully deployed the env would have to be set up to retain the Fernet seed and have it not be hardcoded in the git repository.

Issues may also arise if the product was deployed on a local wifi network, as ports may not be set up to properly interface with the IP/TCP protocol.

### Deployment
*Also can be seen in README*

To deploy the product after ensuring the issues are fixed, simply run main.py and open the assigned address, ensuring that it is also available outside of your local network.
