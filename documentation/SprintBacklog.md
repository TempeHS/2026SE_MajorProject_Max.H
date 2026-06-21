# Sprint-1-database

## Sprint Goal:
* Add basic files structure, add preliminary tables based on data diocntaries and suspected values


## commited items
| backlog ID | User request | 
| --- | --- |
|PB |  |


## Sprint plan: 
* fill out suspected html skeleton
* add log manager basic routes
* add main.py basic routes
* fill out initial documentation, gantt chart, product ideation


## Unit Tests:
NA



## Client feedback summary
* theres not much to comment on - database setup looks good, - still holding discussion about what the final product should look like

# Response
* more discussion with clients about what the final product should do


## sprint summary/review
* added database/table structure
* added basic routes to main.py and logmanager

sprint 1 goals mostly achieved, basic html routes in main.py and their respective html pages are added, mostly just as decorations with no functiuonaility


## issues and difficulties 
*ive completely forgotten how to write html code so I have to relearn how to do that


## evidence 


## sprint retrospective 
* use time better
* better planning weill ebale better workflow
* add in more nesaccary html pages
* fix any errors that may arise

_________________________________________________________________________________________________________________________

# Sprint-2-ui

## Sprint Goal:
* add frontend webpages workflow, along with theuir respective routes and any logmanager methods


## commited items
| backlog ID | User request | 
| --- | --- |
|PB |  |


## Sprint plan: 
*  Create the suspected frontend html files
* fill main.py with html routes
* fix any errors in database
* fill out html with example pages to visualise product
* add example server to database and render to visual product


## Unit Tests:
NA


## Client feedback summary
* webpages are easy to navigate, placeholder serverlist needs to have different data sets in final impementation, being able to signup might be useful

# Response
* next sprint will include a login, signup feature as well as improving the sqlite3 schema


## sprint summary/review
* added and changed html layout, added base, navbar, search, leadernboard, mainpage(redundant)

sprint 2 goals achieved to basic functinaility, probably shouldve filled out more ofit, but am unsure of what maybe required in the future


## issues and difficulties 
* Still having trouble remembering how to write html code, started using previous projects as examples


## evidence


## sprint retrospective
* better plans means better workflow
* add in proper server add feature in next sprint
* fix any errors that may arise

_________________________________________________________________________________________________________________________

# Sprint-3-connections

## Sprint Goal:
* connect database up to frontend, add basic security features for login and signup


## commited items
| backlog ID | User request | 
| --- | --- |
|PB |  |


## Sprint plan: 
* add functionaility for adding a server
* fix database schema to using cascading tables - based on data dictoinaries and unit tests
* add strub routes for login and server addition routes and htmls


## Unit Tests:
| Test ID | Test Name |	What It Tests  |	Input	| Expected Output	| Actual Output |	Pass / Fail |
| --- | --- | --- | --- | --- | --- | --- |
| T3-01 | Valid User Signup | `check_User` / `add_User` — new account creation with unique email | New unique email + any password | Returns False from `check_User`; `add_User` inserts row and returns True | `check_User` returns False; `add_User` inserts hashed password and returns True | Pass |
| T3-02 | Duplicate Email Rejection | `check_User` — duplicate email guard before signup | Email already present in Logins table | `check_User` returns True; signup branch shows "email already used" and makes no insert | `check_User` returns True; duplicate insert is blocked and message is displayed | Pass |


## Client feedback summary
* the frontpage is only rendnering part of the data needed, even if it is a palceholder, probably add a way to add your own servers

# Response
* that will happen later


## sprint summary/review
* fixed sqlite3 table schema, and added more tables
* fixed html referencing, added more functionaility to base page, navabar and leaderbiard
* added/fixed routes in main and log manager

sprint 3 goals fully achieved, database schema and frontend connectivity work to a basic degree, security features are simple and safe


## issues and difficulties 
*sqlite3 code schema is becoming tougher to visualise, 
*data dictionaries are now out of date


## evidence


## sprint retrospective
* the good
  * security features added means user data is safer in case of data breach
* the bad
  * still very little actual functionaility
* the future
  * add more compelte additions rather then just empty deocartions that can be fixed later  

_________________________________________________________________________________________________________________________

# Sprint-4-frontend

## Sprint Goal:
* intitialy fix any errors that may have arisen from the previous sprints, complete login/signup methods and pages with secure hashing and user checks, also add decorater functions for more security


## commited items
| backlog ID | User request | 
| --- | --- |
|PB |  |

## Sprint plan: 
* fix any obvious issues
* add secure hashing to logins/signup route


## Unit Tests:
| Test ID | Test Name |	What It Tests  |	Input	| Expected Output	| Actual Output |	Pass / Fail |
| --- | --- | --- | --- | --- | --- | --- |
| T4-01 | Valid Login | `login_user` — bcrypt password verification on correct credentials | Registered email + correct plaintext password | `login_user` returns True; session stores email and userID | bcrypt.checkpw passes; session is populated and user is redirected to /search | Pass |
| T4-02 | Invalid Password Rejected | `login_user` — bcrypt rejects wrong password for existing email | Registered email + incorrect password | `login_user` returns False; "Invalid email or password" message shown; no session set | bcrypt.checkpw fails; function returns False; no session created | Pass |
| T4-03 | Unauthenticated Route Redirect | `login_required` decorator — blocks access to protected routes without a session | GET /myservers.html with no active session | Request is redirected to /login | Decorator detects missing 'email' key in session and redirects to login | Pass |


## Client feedback summary
* login and signup work, i can log in and see the main page (base,navbar,search) and logout, sqlite3 table looks a lot better filled out, please add functionaility to add a server next

# Response
*next step is to be able to have users add their own servers and render the details


## sprint summary
* added login page and html page
* increase security on login and signup
* added decorator and login/session checks so only some pages are available

sprint 4 goals mostly achieved, errors are fixed, and frontend flow works and can be used


## issues and difficulties 
*at this point the log manager was becoming more filled up and the code itself was becoming more compelx

## evidence 


## sprint retrospective
* the good
  * login and signup work compelete with secure archeticture
* the bad
  * functinaility of peices is still missing
* the future
  * add more compelte additions rather then just empty deocartions that can be fixed later  

_________________________________________________________________________________________________________________________

# Sprint-5-serveradd

## Sprint Goal:
* intitialy fix any issues from previous sprint, need to add the ability for users to add their own servers making sure to properly encrypt and key infomation such as master key, current sqlite schema cannot handle server details so that needs to be fixed, also need to clean up html schema and add main and log manager functions to pass the data 
* sub goal, attempt to curl an active minecraft server from github codespace/container


## commited items
| backlog ID | User request | 
| --- | --- |
|PB |  |


## Sprint plan: 
* fix previous issues
* add server adding html, server list for users
* fix search, and navbar htmls to work with new schema
* add mcwebapi with basic functionaility to see if server is curlable
* fix/add sqlite tables to handle new data types and more infomation + cascading table schema
* attempt to work out how to curl active minecraft server


## Unit Tests:
| Test ID | Test Name |	What It Tests  |	Input	| Expected Output	| Actual Output |	Pass / Fail |
| --- | --- | --- | --- | --- | --- | --- |
| T5-01 | Server Addition — Valid Input | `add_server_details` — inserts server and encrypts master key at rest | Valid serverName, host, port (25565), masterkey, userID; isPrivate = 1 | Returns (True, "Server added successfully."); serverDetails.secretKey stored as Fernet token, not plaintext | Row inserted in servers and serverDetails; secretKey is encrypted ciphertext | Pass |
| T5-02 | Server Addition — Invalid Port | `main.py` serveradd route — port boundary validation before DB insert | serverPort = 0 (out of range) | "Port must be a number between 1 and 65535." displayed; no DB insert | ValueError raised by int conversion check; error message rendered; no insert attempted | Pass |
| T5-03 | Master Key Decrypt Round-Trip | `_encrypt` / `_decrypt` — Fernet encrypt then decrypt returns original value | Plaintext string 'test-master-key-abc123' | `_decrypt(_encrypt(value))` == original value | Fernet token successfully decrypted back to original plaintext | Pass |


## Client feedback summary
* the frontend still isnt rendering all the details properly, but the addition of being able to add servers is good, might want to be able to edit them though

# Response
* in the next sprint i will add an editing feature, as well as proeprly show all the details which we have discussed needs to be shown


## sprint summary
* fixed previous issues
* added server adding functionaility when logged in
* figured out how to curl a server from terminal using port ip and master key
* added my servers html as a decoration, no functionailty
* added mcwebapi which should work now that curling has been fixed
* added encryption and decryption methods to log manager
* added functionly server add method to main

sprint 5 goal fully achieved, sqlite3 tables now have proper schema, curling requests from github were tested and compeleted, 


## issues and difficulties 
*imported librarie methods are becomming very confusing as there is so much itner communication between my built functions and imported ones

## evidence


## sprint retrospective
* the good
  * server addition works
  * api is mostly built
  * curling was tested and fixed
  * asafer encyption of specific data
* the bad
  * still needs certain parts
  * stop wasting time
* the future
  * add more compelte additions rather then just empty deocartions that can be fixed later  

_________________________________________________________________________________________________________________________

# Sprint-6-serverlisten

## Sprint Goal:
* to finish the event listener, so that players can add a server, start the event listener, webapi will take all relevant events and add them, or tally them to the database, then users can end the evenet listener and view the server, serverkills and player statistics


## commited items


## Sprint plan: 
* fix any previous issues
* add all event listener types and their respective methods and functions
* simplify funtions into smaller functions inside log manager
* fix the displying of data
* ensure curl works with other servers
* run general limit tests
* stop the pain


## Unit Tests:
| Test ID | Test Name |	What It Tests  |	Input	| Expected Output	| Actual Output |	Pass / Fail |
| --- | --- | --- | --- | --- | --- | --- |
| T6-01 | Ownership Check on Delete | `delete_server` — prevents a user deleting another user's server | serverID belonging to userID 111111; delete attempted by userID 222222 | Returns (False, "Server not found or you do not own it."); row not deleted | Ownership SELECT returns no row; function returns failure tuple; DELETE not executed | Pass |
| T6-02 | Player Sync from Join Events | `sync_all_log_events` — join events add new players; existing players not duplicated | Log with two join events for 'sphisi' and 'alex'; both absent from players table | Two rows inserted in players; players_msg reports "2 new player(s)" | Both players inserted; duplicate join for same player skipped on subsequent sync | Pass |
| T6-03 | Death Counter Increment | `sync_all_log_events` — death events increment deathCount for existing player | Player 'sphisi' already in players table (deathCount = 0); log contains one death event for 'sphisi' | deathCount for 'sphisi' updated to 1 | UPDATE with COALESCE increments deathCount from 0 to 1 | Pass |
| T6-04 | Kill–Death Pairing Within 2 s | `_parse_log` — game event + death event within 2 seconds are matched as a PvP kill | game event 'sphisi was slain by alex' at T+0.0 s; death event for 'sphisi' at T+1.5 s | kills list contains one entry: killerName='alex', killedName='sphisi' | `_ts_diff_seconds` within threshold; kill candidate paired with death confirmation | Pass |
| T6-05 | Kill–Death Pairing Exceeds 2 s | `_parse_log` — game and death events more than 2 seconds apart are NOT matched | game event at T+0.0 s; death event for same player at T+3.0 s | kills list is empty; no spurious kill recorded | `_ts_diff_seconds` = 3.0 > threshold; candidate discarded | Pass |
| T6-06 | Last-Sync Timestamp Filters Old Events | `sync_all_log_events` — events timestamped before lastSyncTs are ignored on re-sync | Log with one join event at T1; lastSyncTs set to T1; sync called again | No new players inserted; msg reports "No new join events." | `_parse_log` skips entries where ts <= last_sync_ts; no duplicate insert | Pass |
| T6-07 | Malformed Log Lines Ignored | `_parse_log` — invalid JSON lines in event log do not raise exceptions | Log file containing `{not-json}` on one line alongside valid records | json.JSONDecodeError caught; malformed line skipped; valid records still processed | try/except around json.loads continues to next line without crash | Pass |
| T6-08 | Leaderboard Shows Only Public Servers | `get_leaderboard_groups` — isPrivate = 1 servers excluded from public leaderboard | Two servers in DB: one public (isPrivate=0), one private (isPrivate=1); both have kill records | `get_leaderboard_groups` returns only the public server's kill data | SQL WHERE isPrivate = 0 filters out private server; only public kills returned | Pass |


## Client feedback summary
*login and sign up work well enough, still might want to add some restrictions on it, it displays all of the nessacary data, though functionaility for private servers could be good for a future update, searching through servers works, yeah everything works well ernough

# Response
* great


## sprint summary
* fixed any previous issues
* added minor testing file (curl command)
* fixed mcwebapi functinaility, curl commands now get properly built inside log manager and passed to mcwebapi which now can connect to my testing mc server (port wasnt forwarded)
* added logging functionaility for, player kills, palyer deaths, player life count, players unique to server, player vs player interactions unique to server,
* added last sync time so old data wouldnt get added twice on sync
* combined all sync functions so now every event is check and added at once
* Fixed up routes for editing servers
* added nesasarry functions in log manager
* fixed rendering of servers, now renders server | server players | serverkills

sprint 6 goals fully achieved website is compeltely functional, so long as user setsup port forwarding correctly, it just works now with very few visible issues


## issues and difficulties 
* main issues are that the log manager was becomming bloated with functions, so i ahd to merge a couple of them together and simplify various ones
* had an issues where server statistics would render twice for a while because of a build of different html extend blocks across the different html pages
* curl wasnt that hard yay

## evidence


## sprint retrospective
* the good
  * website works completely
  * many edge cases can be caught
  * data base is secure on multiple levels
  * can render servers
  * compeltelty user friendly
* the bad
  * still a bit ugly looking
* the future

_________________________________________________________________________________________________________________________

# future additions and product deployment specifications

## future additions would include a nicer looking ui, stricter password and email requirements, better handling of edge cases, a wider array of event type listeners so more data can be displayed

## Product deployment

# issues

Currently the fernet encryption seed is hardcoded in, this key encrypts the masterkey used to send curl requests to the mcrest api, it is currently hardcoded as having it in the env variable would delete the key on startup and thus the master key wouldnt get properly decrypted and the curl requests would fail. 
if the product were to be fully deployed the env would ahve to be setup to retain the fernet seed and ahve it not be hardcoded in the git repository

issues may also arise if the product was deployed on a local wifi network, as ports may not be setup to properly interface with the ip/tcp protocl

# deployment
*also can be seen in readme*

to deploy the product after ensuring the issue are fixed, simply run main.py and open the assigned address ensuring that it is also available outside of your local network
