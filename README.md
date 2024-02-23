# Minecraft Server Web API
This project is a server-side python script to run a minecraft server and take web api requests to execute commands on the server.

NOTE: This is intended for use with a minecraft (bedrock edition) dedicated server.

## API Documentation

The authorization is a very basic key system.

All APIs will return 401 on an incorrect Authorization header.

All applicable APIs will return 400 if the minecraft server has not been started.

### Domain: 
`https://<address>:<port>/`

### Endpoints:
`api` (GET) - Tests if the api is running. Returns status `200` on sucess.

`api/start` (POST) - Start the minecraft server. Returns status `200` on sucess.

`api/enable_shutdown` (POST) - Enables shutting down the minecraft server when there is no players. Returns status `200` on sucess.

`api/command` (POST) - Executes minecraft command on the server. Uses `command` json data for the command to execute. Returns data in the `command_output` key. Returns status `200` on sucess.

`api/log` (GET) - Returns the last lines from log. Use `lines` json data to denote how many lines to return. Default 15. Returns data in 'log' key. Returns status `200` on sucess.

`api/errorlog` (GET) - Returns the last lines from error log. Use `lines` json data to denote how many lines to return. Default 15. Returns data in 'log' key. Returns status `200` on sucess.
