# MC LEADERBOARDS

MC LEADERBOARDS is a webapp designed so you can view a servers statistics at any time, specifcally create for the Flase life server, MC LEADERBOARDS once setup keeps track of all player on a server their deaths, kills, and life count, as well as server kills and other statistics. 

## Project status
Current status: documenting

Last status: sprint-6-serverlisten

Planned improvments: Finished

## functions and logs

Sprint Documentation
> [documentation/SprintBacklog.md](https://github.com/TempeHS/2026SE_MajorProject_Max.H/blob/main/documentation/SprintBacklog.md)

Product Backlogs Documentation
>[documentation/ProductBacklog.md](https://github.com/TempeHS/2026SE_MajorProject_Max.H/blob/main/documentation/ProductBacklog.md)

Functions Documentation
>[documentation/functions.md](https://github.com/TempeHS/2026SE_MajorProject_Max.H/blob/main/documentation/functions.md)

## Dependencies
MCRESTAPI
FabricAPI
Fabric server loader

Webapi dependncies can be found in requirements.txt

## Installtion and setup

# Setting up the webapp
1. Clone repository
2. remove hardcoded key (security risk)
3. run the following
   > python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   > 
   > export SERVER_FERNET_KEY='PASTE_GENERATED_KEY_HERE'
   > 
   > echo "export SERVER_FERNET_KEY='PASTE_GENERATED_KEY_HERE'" >> ~/.bashrc
   > 
   > chmod 600 ~/.bashrc
   > 
   > source ~/.bashrc
5. run the application, ensuring that the port is correctly forwarded


# setting up a server in the webapp
1. setup a mc fabric server using the mod MCREST API by Natxo09
  > https://github.com/Natxo09/mcrestapi/tree/main
2. start the server as you normally would and record the master key which is created on first startup in the terminal
3. go into the config folder and change the MCRESTAPI.json
4. change the bindm address from a local only to 0.0.0.0 (not a security risk)
5. set CORS to true
6. and set the port to a free port
7. setup the port forwarding for the MCRESTAPI port
8. Login/Signup and press addserver
9. put in the server details !ip is your external ip address, you can find this by using whatsmyipaddress.com
10. click create and go to the my servers page
11. make sure the server is running then press start, this starts the event listener
12. at any time press sync, to update the servers staistics
13. once you have finished the session click end to stop the event listener
14. now you can view the statistics of your server so long as the privacy is set to public, this can be changed in the my servers edit page
