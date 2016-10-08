import json
import os

import requests
from flask import Flask
from flask import request
from flask_cors import CORS
from threading import Timer

from alquistCommunication import send_to_alquist
from userAttributesMemory import get_user_dialogue_state, actualize_user_dialogue_state

flask = Flask(__name__)
cors = CORS(flask)


# verifying of facebook connection
@flask.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "OK", 200


# handling of incoming message from facebook
@flask.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                # someone sent us a message
                if messaging_event.get("message"):
                    # the facebook ID of the person sending you the message
                    sender_id = messaging_event["sender"]["id"]
                    # the recipient's ID, which should be your page's facebook ID
                    recipient_id = messaging_event["recipient"]["id"]
                    # the message's text
                    message_text = messaging_event["message"]["text"]

                    # load users attributes from memory
                    user_attributes = get_user_dialogue_state(sender_id)
                    next_state = user_attributes["state"]

                    # if button was clicked, load it's parameters
                    if "quick_reply" in messaging_event["message"]:
                        message_text = ""
                        next_state = messaging_event["message"]["quick_reply"]["payload"]

                    # send user's message to alquist and obtain it's answer
                    alquist_response = send_to_alquist(user_attributes["session"],
                                                       message_text,
                                                       user_attributes["context"],
                                                       next_state)

                    # actualize memory of user
                    actualize_user_dialogue_state(sender_id, alquist_response)
                    #send response of alquist to user
                    send_messages(sender_id, alquist_response["messages"])

                # delivery confirmation
                if messaging_event.get("delivery"):
                    pass

                # optin confirmation
                if messaging_event.get("optin"):
                    pass

                # user clicked/tapped "postback" button in earlier message
                if messaging_event.get("postback"):
                    pass

    return "OK", 200


# send message to user
def send_messages(sender_id, messages):
    # delay of messages
    cumulated_delay = 0
    for i in range(0, len(messages)):
        # TODO the first message is button
        # if message is text
        if messages[i]['type'] == 'text':
            # if we have some message to show, then show three dots
            if i < len(messages) - 1:
                t = Timer((cumulated_delay + 500.0) / 1000.0, set_typing, [sender_id])
                t.start()
            # if the delay between messages is too short, make it bigger to preserve the order of messages
            if messages[i]['delay'] < 100:
                messages[i]['delay'] = 100
            # add relative delays to cumulated (absolute) delay
            cumulated_delay += messages[i]['delay']

            # append all following buttons to the message before them
            buttons = []
            j = i + 1
            while j < len(messages) and messages[j]['type'] == 'button':
                buttons.append(messages[j]['payload'])
                j += 1

            # send message
            if cumulated_delay > 0:
                t = Timer(cumulated_delay / 1000, send_message, [sender_id, messages[i]["payload"]["text"], buttons])
                t.start()
            else:
                send_message(sender_id, messages[i]["payload"]["text"], buttons)
            i = j


# send message to facebook
def send_message(sender_id, message_text, buttons):
    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}
    quick_replies = []
    data = {
        "recipient": {
            "id": sender_id
        },
        "message": {
            "text": message_text
        }
    }
    # append buttons to message
    for button in buttons:
        quick_replies.append({"content_type": "text", "title": button['label'], 'payload': button["next_state"]})
    if quick_replies:
        data['message'].update({"quick_replies": quick_replies})
    data = json.dumps(data)
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    print(r.headers)


# shows three dots
def set_typing(sender_id):
    params = {"access_token": os.environ["PAGE_ACCESS_TOKEN"]}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "sender_action": "typing_on"
    })
    requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
