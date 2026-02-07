from typing import Any
from app.events import EventDispatcher


class FakeEventDispatcher(EventDispatcher):
    """A fake dispatcher for testing purposes"""

    def __init__(self):
        super().__init__()
        self.emitted_events: list[Any] = []

    async def emit(self, event: Any) -> None:
        """Override emit to store emitted events for assertions in tests"""
        self.emitted_events.append(event)
        await super().emit(event)
