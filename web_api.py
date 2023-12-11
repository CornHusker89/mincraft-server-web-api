
import flask
from flask_limiter import Limiter
import os
import asyncio
import threading
import traceback

from minecraft_server import server as start_minecraft_server, send_command



__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# get enviroment variables
if not os.getenv("API_KEY"):
    raise Exception("Please set the API_KEY environment variable")
else:
    api_key = os.getenv("API_KEY")

if not os.getenv("HTTPS_CERTIFICATE_PATH"):
    raise Exception("Please set the HTTPS_CERTIFICATE_PATH environment variable")
else:
    cert_path = os.getenv("HTTPS_CERTIFICATE_PATH")

if not os.getenv("HTTPS_KEY_PATH"):
    raise Exception("Please set the HTTPS_KEY_PATH environment variable")
else:
    key_path = os.getenv("HTTPS_KEY_PATH")


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


#    if api_key == flask.request.headers.get("API_KEY"):

# api routes
@app.route('/api')
async def index():
    return flask.jsonify('API is online!')



@limiter.limit("3/30 seconds")
@app.route("/api/start", methods=["POST"])
async def start():

    def start_server():
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.create_task(start_minecraft_server())
        loop.run_forever()
        
    thread = threading.Thread(target=start_server)
    thread.start()
    return flask.jsonify({}), 204



@app.route("/api/command", methods=["POST"])
@limiter.limit("50/30 seconds")
async def command():
    command = flask.request.json["command"]

    try:
        if type(command) == str:
            command = [command]
        response = await send_command(command)
        return flask.jsonify({"command_output": response}), 200
    
    except Exception as e:
        print(traceback.format_exc())
        return flask.jsonify({"error": traceback.format_exc()}), 500


@app.route("/api/players", methods=["GET"])
@limiter.limit("15/30 seconds")
async def names():
    data = {"names": ["test1", "test2", "test3"]}
    return flask.jsonify(data)



if __name__ == "__main__":
    context = (cert_path, key_path) # certificate and key files
    app.run(debug=True, port=3536, ssl_context=context)