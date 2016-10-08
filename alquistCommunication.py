import json

import requests
from config import config


# send message to Alquist
def send_to_alquist(session_id, message_text, context, state):
    params = {}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "session": session_id,
        "text": message_text,
        "context": context,
        "state": state
    })
    r = requests.post(config["alquist_url"], params=params, headers=headers, data=data)
    return r.json()
