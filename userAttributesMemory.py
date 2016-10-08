# memory of users
users_dialogue_state = {}


# gets user's dialogue state from memory or it creates new if it doesn't exist already
def get_user_dialogue_state(facebook_user_id):
    if facebook_user_id in users_dialogue_state:
        return users_dialogue_state.get(facebook_user_id)
    else:
        users_dialogue_state.update({facebook_user_id: {"session": "", "context": {}, "state": "init"}})
        return users_dialogue_state.get(facebook_user_id)


# save new user's dialogue state to memory
def actualize_user_dialogue_state(facebook_user_id, alquist_response):
    users_dialogue_state.update({facebook_user_id: {"session": alquist_response["session"],
                                                    "context": alquist_response["context"],
                                                    "state": alquist_response["state"]}})
