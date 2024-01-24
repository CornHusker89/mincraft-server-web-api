
import flask
from flask_limiter import Limiter
from waitress import serve
import os
import asyncio
import threading
import traceback

from minecraft_server import server as start_minecraft_server, player_check as start_autoshutdown, send_command, log, error_log

import dotenv
env_path = dotenv.find_dotenv()
env_values = dotenv.dotenv_values(env_path)

# get enviroment variables
api_key = env_values["API_KEY"]
port = env_values["PORT"]
cert_path = env_values["HTTPS_CERTIFICATE_PATH"]
key_path = env_values["HTTPS_KEY_PATH"]


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


minecraft_server_started: bool = False


# load flask
def get_proxy_remote_address():
    """
    :return: the ip address for the current request (or 127.0.0.1 if none found)
    """
    if flask.request.headers.get("X-Forwarded-For") != None:
        return str(flask.request.headers.get("X-Forwarded-For"))
    return flask.request.remote_addr or "127.0.0.1"

app = flask.Flask(__name__)
limiter = Limiter(
    get_proxy_remote_address,
    app=app,
    storage_uri="memory://",
)



# api routes
@app.route('/api', methods=["GET"])
@limiter.limit("50/30 seconds")
async def index():
    if f"Bearer {api_key}" != flask.request.headers.get("Authorization"): return flask.jsonify({"error": "Invalid Authorization"}), 401
    return flask.jsonify({"message": "API is online!"}), 200




@app.route("/api/start", methods=["POST"])
@limiter.limit("3/30 seconds")
async def start():
    if f"Bearer {api_key}" != flask.request.headers.get("Authorization"): return flask.jsonify({"error": "Invalid Authorization"}), 401
    global minecraft_server_started
    if minecraft_server_started: return flask.jsonify({"error": "The minecraft server has already been started"}), 400
    def start_server():
        global minecraft_server_started
        minecraft_server_started = True
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.create_task(start_minecraft_server())
        loop.run_forever()
        
    thread = threading.Thread(target=start_server)
    thread.start()
    return flask.jsonify({"message": "Server has been started"}), 204



@app.route("/api/enable_shutdown", methods=["POST"])
@limiter.limit("3/30 seconds")
async def autoshutdown():
    if f"Bearer {api_key}" != flask.request.headers.get("Authorization"): return flask.jsonify({"error": "Invalid Authorization"}), 401
    global minecraft_server_started
    if not minecraft_server_started: return flask.jsonify({"error": "The minecraft server has not been started"}), 400
    def enable_autoshutdown():
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.create_task(start_autoshutdown())
        loop.run_forever()
        
    thread = threading.Thread(target=enable_autoshutdown)
    thread.start()
    return flask.jsonify({"message": "Automatic shutdown has been enabled"}), 204



@app.route("/api/command", methods=["POST"])
@limiter.limit("80/30 seconds")
async def command():
    if f"Bearer {api_key}" != flask.request.headers.get("Authorization"): return flask.jsonify({"error": "Invalid Authorization"}), 401
    global minecraft_server_started
    if not minecraft_server_started: return flask.jsonify({"error": "The minecraft server has not been started yet"}), 400
    try:
        command = flask.request.json["command"]
    except KeyError:
        return flask.jsonify({"error": "\"command\" key was not found in the request json"}), 400

    try:
        if type(command) == str:
            command = [command]
        response = await send_command(command)
        return flask.jsonify({"command_output": response}), 200
    
    except Exception as e:
        error_log(traceback.format_exc())
        return flask.jsonify({"error": "An error occurred"}), 500



@app.route("/api/log", methods=["GET"]) 
@limiter.limit("30/30 seconds")
async def get_log():
    if f"Bearer {api_key}" != flask.request.headers.get("Authorization"): return flask.jsonify({"error": "Invalid Authorization"}), 401
    try:
        # the amount of lines they requested to see
        requested_lines = flask.request.json["lines"]
    except:
        requested_lines = 15

    # make sure that the requested lines is a valid number
    try:
        requested_lines = int(requested_lines) * -1
    except:
        return flask.jsonify({"error": "The amount of lines requested must be a number"}), 400

    try:
        with open(os.path.join(__location__, "log.txt"), "r") as file:
            lines = file.readlines()
            last_lines = lines[requested_lines:]
            return flask.jsonify({"log": "".join(last_lines)}), 200
    except Exception as e:
        error_log(traceback.format_exc())
        return flask.jsonify({"error": "An error occurred"}), 500



@app.route("/api/errorlog", methods=["GET"]) 
@limiter.limit("30/30 seconds")
async def get_error_log():
    if f"Bearer {api_key}" != flask.request.headers.get("Authorization"): return flask.jsonify({"error": "Invalid Authorization"}), 401
    try:
        # the amount of lines they requested to see
        requested_lines = flask.request.json["lines"]
    except:
        requested_lines = 15

    # make sure that the requested lines is a valid number
    try:
        requested_lines = int(requested_lines) * -1
    except:
        return flask.jsonify({"error": "The amount of lines requested must be a number"}), 400

    try:
        with open(os.path.join(__location__, "error_log.txt"), "r") as file:
            lines = file.readlines()
            last_lines = lines[requested_lines:]
            return flask.jsonify({"log": "".join(last_lines)}), 200
    except Exception as e:
        error_log(traceback.format_exc())
        return flask.jsonify({"error": "An error occurred"}), 500



if __name__ == "__main__":
    context = (cert_path, key_path) # certificate and key files
    #app.run(debug=True, port=port, ssl_context=context)
    print("starting server on port " + str(port))
    serve(app=app, host='0.0.0.0', port=port, url_scheme="https")