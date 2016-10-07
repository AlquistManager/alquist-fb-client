# memory of users
users_dialogue_state = {}


# gets user's dialogue state from memory or it creates new if it doesn't exist already
def get_user_dialogue_state(facebook_user_id):
    if facebook_user_id in users_dialogue_state:
        users_dialogue_state.get(facebook_user_id)
    else:
        users_dialogue_state.update({facebook_user_id: {"session_id": "", "context": {}, "actual": "init"}})


# save new user's dialogue state to memory
def actualize_user_dialogue_state(facebook_user_id, alquist_response):
    users_dialogue_state.update({facebook_user_id: {"session_id": alquist_response["session_id"],
                                                "context": alquist_response["context"],
                                                "actual": alquist_response["state"]}})
