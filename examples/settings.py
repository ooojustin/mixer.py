import sys
sys.path.append('..')

import os
import json
import time

from mixer.api import MixerAPI

def file_exists(file):
    if not os.path.exists(file):
        return False
    if not os.path.isfile(file):
        return False
    return True

def read_file(file):
    return open(file).read()

def write_file(file, text):
    file = open(file, "w")
    file.write(text)
    file.close()

def save(data):
    settings_raw = json.dumps(data, indent = 4)
    write_file("settings.cfg", settings_raw)

def init():

    settings = dict()
    settings["channel_name"] = input("channel name: ")
    settings["client_id"] = input("client id: ")
    settings["client_secret"] = input("client secret: ")
    api = MixerAPI(settings["client_id"], settings["client_secret"])

    shortcode = api.get_shortcode([
    "chat:bypass_catbot", "chat:bypass_filter", "chat:bypass_links",
    "chat:bypass_slowchat", "chat:cancel_skill", "chat:change_ban",
    "chat:change_role", "chat:chat", "chat:clear_messages",
    "chat:connect", "chat:edit_options", "chat:giveaway_start",
    "chat:poll_start", "chat:poll_vote", "chat:purge",
    "chat:remove_message", "chat:timeout", "chat:view_deleted",
    "chat:whisper"])

    url = "https://mixer.com/go?code=" + shortcode["code"]
    print("visit the following url:", url)

    while True:
        time.sleep(10)
        response = api.check_shortcode(shortcode["handle"])
        status_code = response.status_code
        if response.status_code == 200:
            authorization_code = response.json()["code"]
            print("authorization_code:", authorization_code)
            break

    tokens = api.get_token(authorization_code)
    print("access_token:", tokens["access_token"])
    print("refresh_token:", tokens["refresh_token"])

    settings["access_token"] = tokens["access_token"]
    settings["refresh_token"] = tokens["refresh_token"]
    save(settings)


def load():

    if not file_exists("settings.cfg"):
        init()

    settings_raw = read_file("settings.cfg")
    settings = json.loads(settings_raw)
    return settings

def update_tokens(access_token, refresh_token):
    settings = load()
    settings["access_token"] = access_token
    settings["refresh_token"] = refresh_token
    save(settings)
