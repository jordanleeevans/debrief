import asyncio
from app.tests.mocks import FakeEventDispatcher


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
        self.dispatcher = FakeEventDispatcher()

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


class FakeAttachment:
    def __init__(self, data: bytes, size: int | None = None):
        self._data = data
        self.size = len(data) if size is None else size

    async def read(self):
        return self._data


class FakeAuthor:
    def __init__(self, id: int = 123, name: str = "Tester"):
        self.id = id
        self.name = name


class FakeMessage:
    def __init__(
        self,
        id: int = 1,
        attachments: list | None = None,
        author: FakeAuthor | None = None,
    ):
        self.id = id
        self.attachments = attachments or []
        self.author = author or FakeAuthor()
        self.content = ""


class FakeChannel:
    def __init__(self, id: int = 456):
        self.id = id


class FakeCtx:
    def __init__(
        self,
        message: FakeMessage | None = None,
        author: FakeAuthor | None = None,
        bot: FakeBot | None = None,
        channel: FakeChannel | None = None,
    ):
        self.message = message or FakeMessage()
        self.author = author or self.message.author
        self.bot = bot or FakeBot()
        self.channel = channel or FakeChannel()
        self.sent: list[str] = []

    async def send(self, content: str):
        self.sent.append(content)
