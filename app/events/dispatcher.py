import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class EventDispatcher:
    """Simple event dispatcher for decoupled communication"""

    def __init__(self):
        self.handlers: dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable) -> None:
        """Subscribe a handler to an event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type.__name__}")

    async def emit(self, event: Any) -> None:
        """Emit an event and call all registered handlers"""
        event_type = type(event)
        logger.debug(f"Emitting event: {event_type.__name__}")

        if event_type not in self.handlers:
            logger.debug(f"No handlers registered for {event_type.__name__}")
            return

        for handler in self.handlers[event_type]:
            try:
                logger.debug(f"Calling handler: {handler.__name__}")
                if hasattr(handler, "__call__"):
                    result = handler(event)
                    # Check if the result is a coroutine (async function)
                    if hasattr(result, "__await__"):
                        await result
            except Exception as e:
                logger.error(
                    f"Error in handler {handler.__name__}: {str(e)}", exc_info=True
                )


# Global dispatcher instance
dispatcher = EventDispatcher()
