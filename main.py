from facebookCommunication import flask, send_message
from config import config

if __name__ == '__main__':
    flask.run(port=int(config["port"]), debug=False, threaded=True)
