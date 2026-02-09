import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class CommandBus:
    """Command bus for executing commands with single handlers.

    Unlike events which can have multiple subscribers, each command
    should have exactly one handler that executes it.
    """

    def __init__(self):
        self.handlers: dict[type, Callable] = {}

    def register(self, command_type: type, handler: Callable) -> None:
        """Register a handler for a command type.

        Raises ValueError if a handler is already registered for this command type.
        """
        if command_type in self.handlers:
            raise ValueError(
                f"Handler already registered for {command_type.__name__}. "
                "Commands should have exactly one handler."
            )
        self.handlers[command_type] = handler
        logger.debug(f"Registered {handler.__name__} for {command_type.__name__}")

    async def execute(self, command: Any) -> Any:
        """Execute a command by calling its registered handler.

        Returns the result from the handler.
        """
        command_type = type(command)
        logger.debug(f"Executing command: {command_type.__name__}")

        if command_type not in self.handlers:
            raise ValueError(
                f"No handler registered for {command_type.__name__}. "
                f"Register a handler using bus.register()"
            )

        handler = self.handlers[command_type]
        try:
            logger.debug(f"Calling handler: {handler.__name__}")
            result = handler(command)
            # Check if the result is a coroutine (async function)
            if hasattr(result, "__await__"):
                return await result
            return result
        except Exception as e:
            logger.error(
                f"Error in command handler {handler.__name__}: {str(e)}", exc_info=True
            )
            raise

    def clear_handlers(self) -> None:
        """Clear all registered handlers (useful for testing)"""
        self.handlers.clear()
        logger.debug("Cleared all command handlers")

    @property
    def registered_commands(self) -> list[type]:
        """Get a list of registered command types"""
        return list(self.handlers.keys())
