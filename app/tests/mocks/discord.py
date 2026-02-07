import asyncio


class FakeBot:
    """A very small fake bot that cooperates with the app lifespan.

    - `start(token)` sets `started` and waits until `close()` is called.
    - `close()` signals the `start` task to finish and records `closed`.
    """

    def __init__(self):
        self.started = False
        self.closed = False
        self.started_with = None
        self._stop_event = asyncio.Event()
        self.cached_channels = {}

    async def start(self, token: str):
        self.started_with = token
        self.started = True
        # wait until close() sets the event
        await self._stop_event.wait()
        self.started = False

    async def close(self):
        self._stop_event.set()
        self.closed = True

    def get_channel(self, channel_id):
        return self.cached_channels.get(channel_id)

    async def fetch_channel(self, channel_id):
        # Simulate an API call to fetch the channel
        channel = self.get_channel(channel_id)
        if channel is not None:
            return channel
        # Simulate fetching from API and caching it
        fake_channel = (
            object()
        )  # Replace with actual channel object in real implementation
        self.cached_channels[channel_id] = fake_channel
        return fake_channel
