import json
import websockets
import inspect

class MixerWS():

    def __init__(self, url, **kwargs):
        self.url = url
        self.on_connected = kwargs.pop("on_connected", None)
        self.kwargs = kwargs

    async def try_call(self, func, *opts):
        """Calls a coroutine function with parameters, if it's defined."""
        if inspect.iscoroutinefunction(func):
            await func(*opts)

    async def connect(self):
        """Establishes connection to websocket endpoint and calls on_connected callback."""
        self.websocket = await websockets.connect(self.url, **self.kwargs)
        await self.try_call(self.on_connected)

    async def send_packet(self, packet):
        """Sends a packet to the server.

        Args:
            packet (dict): Data to be json encoded and send.
        """
        packet_raw = json.dumps(packet)
        await self.websocket.send(packet_raw)

    async def receive_packet(self):
        """dict: Receives a packet from the server."""
        packet_raw = await self.websocket.recv()
        return json.loads(packet_raw)
