import json, asyncio, inspect, logging
from time import time

from . import exceptions as MixerExceptions

class MixerOAuth:

    # array of methods to invoke once access_token is refreshed
    # methods are invoked with 2 params (new access_token/refresh_token)
    _refreshed = list()

    # scheduled task to refresh tokens
    _auto_refresh_task = None

    @classmethod
    async def create(cls, api, access_token, refresh_token):
        self = MixerOAuth()
        self.api = api
        self.access_token = access_token
        self.refresh_token = refresh_token
        await self.update_token_data()
        return self

    async def update_token_data(self):
        data = await self.api.check_token(self.access_token)
        active = data.get("active")
        self.expires = data.get("exp") - 10 if active else -1
        self.user_id = data.get("sub") if active else -1
        self.username = data.get("username") if active else ""

    async def ensure_active(self):
        """Refreshes the access_token if it's not active."""
        if not self.active:
            await self.refresh()

    async def refresh(self, auto_refreshed = False):
        """Refreshes tokens and triggers callbacks w/ new tokens."""

        # refresh tokens
        tokens = await self.api.get_token(self.refresh_token, refresh = True)
        self.access_token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")
        await self.update_token_data()

        # trigger callbacks w/ new tokens
        for event in self._refreshed:
            if inspect.iscoroutinefunction(event):
                await event(self.access_token, self.refresh_token)
            elif inspect.isfunction(event):
                event(self.access_token, self.refresh_token)

        # if this wasn't trigerred by auto-refresh
        # and we have an auto-refresh task running
        # automatically re-register the task
        if (not auto_refreshed
                and self._auto_refresh_task is not None
                and not self._auto_refresh_task.cancelled()
                and not self._auto_refresh_task.done()):
            self._auto_refresh_task.cancel()
            self.register_auto_refresh()

    async def _auto_refresh(self):

        # determine time to wait before a refresh, make sure it's at least 0
        delay = self.expires - time()
        if delay < 0:
            delay = 0

        # sleep until we should refresh the token
        print("waiting {} seconds before automatically refreshing tokens...".format(delay))
        await asyncio.sleep(delay)

        # refresh tokens
        await self.refresh(auto_refreshed = True)

        # schedule this function as a task so we can automatically do it again
        self.register_auto_refresh()

    def register_auto_refresh(self):
        """Registers a task that will endlessly ensure the tokens are valid."""
        self._auto_refresh_task = asyncio.create_task(self._auto_refresh())

    def on_refresh(self, callback):
        """Adds a callback to be triggered when tokens are updated."""
        self._refreshed.append(callback)

    @property
    def header(self):
        """dict: A dictionary containing the oauth bearer token."""
        return { "Authorization": "Bearer {}".format(self.access_token) }

    @property
    def active(self):
        """bool: Indicates if the access_token is still valid."""
        return self.expires > time()
