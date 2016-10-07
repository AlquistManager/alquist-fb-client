import json
import os

import requests
from flask import Flask, app
from flask import request
from flask.ext.cors import CORS

from alquistCommunication import send_to_alquist
from userAttributesMemory import get_user_dialogue_state, actualize_user_dialogue_state

flask = Flask(__name__)
cors = CORS(flask)


# verifying of facebook connection
@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "", 200


# handling of incoming message from facebook
@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    # the recipient's ID, which should be your page's facebook ID
                    recipient_id = messaging_event["recipient"]["id"]
                    # the message's text
                    message_text = messaging_event["message"]["text"]

                    user_attributes = get_user_dialogue_state(sender_id)
                    alquist_response = send_to_alquist(user_attributes["session_id"], message_text,
                                                       user_attributes["context"],
                                                       user_attributes["state"])

                    actualize_user_dialogue_state(sender_id, alquist_response)
                    send_message(sender_id, alquist_response["text"])

                # delivery confirmation
                if messaging_event.get("delivery"):
                    pass

                # optin confirmation
                if messaging_event.get("optin"):
                    pass

                # user clicked/tapped "postback" button in earlier message
                if messaging_event.get("postback"):
                    pass

    return "ok", 200


# send message to facebook
def send_message(recipient_id, message_text):
    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
