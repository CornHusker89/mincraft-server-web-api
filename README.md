# Minecraft Server Web API
This project is a server-side python script to run a minecraft server and take web api requests to execute commands on the server.

NOTE: This is intended for use with a minecraft (bedrock) dedicated server.

## API Documentation

### Domain: 
https://<address>:<port>/

### Endpoints:
api/ (GET) - Tests if the api is running. Returns 200 on sucess
api/start (POST) - Start the minecraft server. Returns 204 on sucess.
api/command (POST) - Executes minecraft command on the server. Returns data in 'command_output' key. Returns 200 on sucess.
api/log (POST) - Returns the last lines from log. Use 'lines' json data to denote how many lines to return. Default 15. Returns data in 'log' key. Returns 200 on sucess.