import sys
sys.path.append('..')

from mixer.api import MixerAPI
from mixer.chat import MixerChat
from mixer.oauth import MixerOAuth

import asyncio
import settings
cfg = settings.load()

api = MixerAPI(cfg["client_id"], cfg["client_secret"])
channel = api.get_channel(cfg["channel_name"])
chat = MixerChat(api, channel.id)

def update_tokens(access_token, refresh_token):
    settings["access_token"] = access_token
    settings["refresh_token"] = refresh_token
    settings.save(settings)

auth = MixerOAuth(cfg["access_token"], cfg["refresh_token"])
auth.refreshed_events.append(update_tokens)

@chat.commands
async def ping(message):
    return "pong!"

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(
    auth.start(api),
    chat.start(auth)
))
