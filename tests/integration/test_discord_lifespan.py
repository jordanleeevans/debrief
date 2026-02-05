import asyncio
import time

import pytest

# Skip if fastapi isn't available in this environment
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app import main
from app.core.settings import settings


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

    async def start(self, token: str):
        self.started_with = token
        self.started = True
        # wait until close() sets the event
        await self._stop_event.wait()
        self.started = False

    async def close(self):
        self._stop_event.set()
        self.closed = True


def test_lifespan_starts_and_stops_bot(monkeypatch):
    fake = FakeBot()
    # Replace the bot used by the app before startup runs
    monkeypatch.setattr(main, "bot", fake)

    # Starting the TestClient triggers the app lifespan which should call
    # `asyncio.create_task(bot.start(...))` and later `await bot.close()` on shutdown.
    with TestClient(main.app) as client:
        # wait briefly for the background start task to run
        deadline = time.time() + 1.0
        while time.time() < deadline and not fake.started:
            time.sleep(0.01)

        assert fake.started is True
        assert fake.started_with == settings.DISCORD_BOT_TOKEN

        # Basic request while the bot is running
        r = client.get("/")
        assert r.status_code == 200

    # After exiting the context the shutdown should have been processed
    deadline = time.time() + 1.0
    while time.time() < deadline and not fake.closed:
        time.sleep(0.01)

    assert fake.closed is True
    assert fake.started is False
