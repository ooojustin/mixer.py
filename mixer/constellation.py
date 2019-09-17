from .ws import MixerWS

class MixerConstellation:

    CONSTELLATION_URL = "wss://constellation.mixer.com"
    websocket = None

    def __init__(self, on_connected):
        self.on_connected = on_connected
        self.callbacks = dict()
        self.packet_id = 0

    async def start(self):
        """Initializes the Constellation websocket and begins to listen for events."""

        self.websocket = MixerWS(self.CONSTELLATION_URL)
        await self.websocket.connect()
        await self.on_connected(self) # call on_connected func (we should probably subscribe to events)

        while True:

            # receive a packet from server
            packet = await self.websocket.receive_packet()

            # make sure it's an event we're subscribed to
            if packet["type"] != "event": continue
            if packet["event"] != "live": continue

            # find and invoke the callback function with the packet & payload
            event_name = packet["data"]["channel"]
            payload = packet["data"]["payload"]
            callback = self.callbacks.get(event_name, None)
            if callback is not None:
                await callback(packet, payload)

    async def subscribe(self, events, callback):
        """Subcribes the Constellation websocket to a list of provided events.

        Args:
            events (list): A list of events to subscribe to.
            callback (function): A callable function to trigger with constellation packet payload when event is triggered.

        Returns:
            int: The unique id used to identify the "livesubscribe" method packet.
        """

        # if a single event is provided, wrap it in a list automatically
        if isinstance(events, str):
            events = [events]

        # build livesubscribe packet
        packet = {
            "type": "method",
            "method": "livesubscribe",
            "params": {
                "events": events
            },
            "id": self.packet_id
        }

        # send packet to server and determine callback
        await self.websocket.send_packet(packet)
        for event in events:
            self.callbacks[event] = callback

        # increment packet id and return unique packet id
        self.packet_id += 1
        return self.packet_id
