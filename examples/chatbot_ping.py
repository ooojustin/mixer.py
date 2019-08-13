import sys
sys.path.append('..')

from mixer.api import MixerAPI
from mixer.chat import MixerChat
from mixer.oauth import MixerOAuth

import asyncio
import settings
cfg = settings.load()

# initialize mixer api and chat client
api = MixerAPI(cfg["client_id"], cfg["client_secret"])
chat = MixerChat(api, cfg["channel_name"])

# initialize oauth wrapper
auth = MixerOAuth(api, cfg["access_token"], cfg["refresh_token"])
auth.on_refresh(settings.update_tokens)
auth.ensure_active()

# define commands
@chat.commands
async def ping(message):
    return "pong!"

# define events
@chat
async def on_ready(username, id):
    print("authenticated: {} [{}]".format(username, id))

# start chat/oauth loops asynchronously
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(
    auth.start(api),
    chat.start(auth)
))
