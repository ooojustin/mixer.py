import sys
sys.path.append('..')

import mixer.exceptions as MixerExceptions
from mixer.api import MixerAPI
from mixer.chat import MixerChat
from mixer.oauth import MixerOAuth

import asyncio
import settings

async def init():

    global api, auth, chat, cfg
    cfg = await settings.load()

    # initialize mixer api and chat client
    api = MixerAPI(cfg["client_id"], cfg["client_secret"])
    chat = await MixerChat.create(api, cfg["channel_name"])

    # initialize oauth wrapper
    try:
        auth = await MixerOAuth.create(api, cfg["access_token"], cfg["refresh_token"])
        auth.on_refresh(settings.update_tokens)
        await auth.ensure_active()
        auth.register_auto_refresh()
    except MixerExceptions.WebException as ex:
        print(ex.status, ex.text)

loop = asyncio.get_event_loop()
loop.run_until_complete(init())

# define commands
@chat.commands
async def ping(message):
    return "pong!"

# define events
@chat
async def on_ready(username, id):
    print("authenticated: {} [{}]".format(username, id))

# start chat/oauth loops asynchronously
loop.run_until_complete(chat.start(auth))
