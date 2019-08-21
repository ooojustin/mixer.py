import json, asyncio, inspect, logging
from time import time

class MixerOAuth:

    # array of methods to invoke once access_token is refreshed
    # methods are invoked with 2 params (new access_token/refresh_token)
    __refreshed = list()

    def __init__(self, api, access_token, refresh_token):
        self.api = api
        self.access_token = access_token
        self.refresh_token = refresh_token

    async def get_token_data(self):
        """dict: Information about the access token."""
        return await self.api.check_token(self.access_token)

    def on_refresh(self, callback):
        """Adds a callback to be triggered when tokens are updated."""
        self.__refreshed.append(callback)

    async def refresh(self):
        """Refreshes tokens and triggers callbacks w/ new tokens."""

        # refresh tokens
        tokens = self.api.get_token(self.refresh_token, refresh = True)
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]

        # trigger callbacks w/ new tokens
        for event in self.__refreshed:
            if inspect.iscoroutinefunction(event):
                await event(self.access_token, self.refresh_token)
            elif inspect.isfunction(event):
                event(self.access_token, self.refresh_token)

    def ensure_active(self):
        """Ensures the access token is active, and refreshes it if it isn't."""
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(self.get_token_data())
        if not data.get("active", False):
            loop.run_until_complete(self.refresh())

    async def start(self, api):
        """Begin an endless loop that constantly ensures token validity."""

        while True:

            # if the token is inactive, refresh it
            token_data = await self.get_token_data()
            if not token_data["active"]:
                await self.refresh()

            # otherwise, automatically refresh it when it's going to expire
            expires_in = int(token_data["exp"] - time() - 10)
            logging.info("waiting ~{} seconds before refreshing access_token".format(expires_in))
            await asyncio.sleep(expires_in)
            await self.refresh()
