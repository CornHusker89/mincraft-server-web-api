
import flask
from flask_limiter import Limiter
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

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


# get enviroment variables
if not os.getenv("API_KEY"):
    raise Exception("Please set the API_KEY environment variable")
else:
    api_key = os.getenv("API_KEY")



# api routes
@app.route('/')
def index():
    return flask.jsonify('API is online!')


@app.route("/api/minecraft/players", methods=["GET"])
@limiter.limit("20/30 seconds")
def names():
    data = {"names": ["test1", "test2", "test3"]}
    return flask.jsonify(data)



if __name__ == '__main__':
    context = ('server_key.crt', 'server_key.key') # certificate and key files
    app.run(debug=True, port=3536, ssl_context=context)