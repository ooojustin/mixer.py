import aiohttp
import dateutil.parser
import json
from datetime import datetime, timezone, timedelta
from enum import Enum

from . import exceptions
from .objects import MixerUser, MixerChannel

class RequestMethod(Enum):
    GET = 0
    POST = 1

class MixerAPI:

    API_URL = "https://mixer.com/api/v1"
    API_URL_V2 = "https://mixer.com/api/v2"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = aiohttp.ClientSession(headers = { "Client-ID": self.client_id })

    async def request(self, method, url, data = None, parse_json = False):

        # pick ... based on request type
        if method is RequestMethod.GET:
            ctx_mgr = self.session.get(url)
        elif method is RequestMethod.POST:
            ctx_mgr = self.session.post(url, json = data)

        async with ctx_mgr as response:

            # handle specific response codes
            if response.status == 404:
                raise MixerExceptions.NotFound("Not found: API returned 404.")

            text = await response.text()
            info = "{} -> {}".format(response.status, text)
            assert response.status == 200, "API returned unhandled status code: " + info

            if not parse_json:
                return text
            else:
                try:
                    return json.loads(text)
                except ValueError:
                    raise RuntimeError("Failed to parse json from response.")

    async def get(self, url, **kwargs):
        coro = self.request(RequestMethod.GET, url, **kwargs)
        return await coro

    def get_channel(self, id_or_token):
    async def post(self, url, data, **kwargs):
        kwargs["data"] = data
        coro = self.request(RequestMethod.POST, url, **kwargs)
        return await coro

        """Retrieves a MixerChannel object from username or channel id.

        Args:
            id_or_token (str): Username (or id) of Mixer channel.

        Returns:
            :class:`mixer.objects.MixerChannel`: Channel information.
        """
        url = "{}/channels/{}".format(self.API_URL, id_or_token)
        response = self.session.get(url)
        if response.status_code == 200:
            channel = MixerChannel(response.json())
            channel.set_api(self)
            return channel
        elif response.status_code == 404:
            raise MixerExceptions.NotFound("Channel not found: API returned 404.")
        else:
            info = "{} -> {}".format(response.status_code, response.text)
            raise RuntimeError("API returned unhandled status code: " + info)

    def get_user(self, user_id):
        """Retrieves a MixerUser object from a user id.

        Args:
            user_id (int): The unique id of a Mixer user.

        Returns:
            :class:`mixer.objects.MixerUser`: User information.
        """
        url = "{}/users/{}".format(self.API_URL, user_id)
        response = self.session.get(url)
        if response.status_code == 200:
            user = MixerUser(response.json())
            user.set_api(self)
            return user
        elif response.status_code == 404:
            raise MixerExceptions.NotFound("User not found: API returned 404.")
        else:
            info = "{} -> {}".format(response.status_code, response.text)
            raise RuntimeError("API returned unhandled status code: " + info)

    def get_shortcode(self, scope = None):
        """Makes a request to begin shortcode oauth process.

        Args:
            scope (list): A list of scope/permissions to generate token with.

        Returns:
            dict: Information to proceed with shortcode oauth process."""
        url = "{}/oauth/shortcode".format(self.API_URL)
        if scope is None: scope = list()
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": " ".join(scope)
        }
        response = self.session.post(url, data)
        return response.json()

    def check_shortcode(self, handle):
        """Check a shortcode handle to determine it's status.

        Args:
            str: Shortcode handle.

        Returns:
            dict: Shortcode status information.
        """
        url = "{}/oauth/shortcode/check/{}".format(self.API_URL, handle)
        response = self.session.get(url)
        return response

    def get_token(self, code_or_token, refresh = False):
        """Generate/refresh tokens.

        Args:
            code_or_token (str): Authorization code or refresh token.
            refresh (bool): Whether or not a refresh token is provided.

        Returns:
            dict: New token(s) + information from server.
        """
        url = "{}/oauth/token".format(self.API_URL)
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        if refresh:
            data["grant_type"] = "refresh_token"
            data["refresh_token"] = code_or_token
        else:
            data["grant_type"] = "authorization_code"
            data["code"] = code_or_token

        response = self.session.post(url, data)
        return response.json() # https://pastebin.com/n1Kjjphq

    def check_token(self, token):
        """Gets information about an existing token.

        Args:
            token (str): An access token or a refresh token.
        """
        url = "{}/oauth/token/introspect".format(self.API_URL)
        data = { "token": token }
        response = self.session.post(url, data)
        return response.json() # https://pastebin.com/SEd6Y2Jz

    def get_broadcast(self, channel_id):
        """Gets an active broadcast on a given chanel.

        Args:
            channel_id (int): Unique channel ID number.
        """
        url = "{}/channels/{}/broadcast".format(self.API_URL, channel_id)
        response = self.session.get(url)
        return response.json()

    def get_uptime(self, channel_id):
        """Gets the uptime of a channels broadcast.

        Returns:
            int: Duration of broadcast in seconds.
        """

        # get broadcast and make sure it's online
        broadcast = self.get_broadcast(channel_id)
        if "error" in broadcast or not broadcast["online"]:
            return None

        # determine the streams start time and current time
        started = dateutil.parser.parse(broadcast["startedAt"])
        now = datetime.now(timezone.utc)

        # calculate delta and remove microseconds because they're insignificant
        delta = now - started
        delta = delta - timedelta(microseconds = delta.microseconds)
        return delta

    # type format: [sparks, embers]-[weekly, monthly, yearly, alltime]
    def get_leaderboard(self, type, channel_id, limit = 10):
        url = "{}/leaderboards/{}/channels/{}?limit={}".format(self.API_URL_V2, type, channel_id, limit)
        response = self.session.get(url)
        return response.json()

    def get_chatters(self, channel_id):
        url = "{}/chats/{}/users".format(self.API_URL_V2, channel_id)
        response = self.session.get(url)
        return response.json()
