import pytest
from app.commands import CommandBus, AnalyzeImagesCommand, QueryDatabaseCommand


class TestCommandBusInit:
    """Test CommandBus initialization"""

    def test_init_creates_empty_handlers(self):
        """Test that CommandBus starts with empty handlers"""
        bus = CommandBus()
        assert bus.handlers == {}
        assert bus.registered_commands == []


class TestCommandBusRegister:
    """Test CommandBus registration"""

    def test_register_command_handler(self):
        """Test registering a command handler"""
        bus = CommandBus()

        def handler(cmd):
            return "handled"

        bus.register(AnalyzeImagesCommand, handler)

        assert AnalyzeImagesCommand in bus.handlers
        assert bus.handlers[AnalyzeImagesCommand] == handler

    def test_register_multiple_different_handlers(self):
        """Test registering multiple different command handlers"""
        bus = CommandBus()

        def handler1(cmd):
            return "handled1"

        def handler2(cmd):
            return "handled2"

        bus.register(AnalyzeImagesCommand, handler1)
        bus.register(QueryDatabaseCommand, handler2)

        assert len(bus.handlers) == 2
        assert bus.handlers[AnalyzeImagesCommand] == handler1
        assert bus.handlers[QueryDatabaseCommand] == handler2

    def test_register_duplicate_handler_raises_error(self):
        """Test that registering a duplicate handler raises ValueError"""
        bus = CommandBus()

        def handler1(cmd):
            return "handled1"

        def handler2(cmd):
            return "handled2"

        bus.register(AnalyzeImagesCommand, handler1)

        with pytest.raises(ValueError) as exc_info:
            bus.register(AnalyzeImagesCommand, handler2)

        assert "Handler already registered" in str(exc_info.value)
        assert "AnalyzeImagesCommand" in str(exc_info.value)

    def test_registered_commands_property(self):
        """Test the registered_commands property"""
        bus = CommandBus()

        def handler(cmd):
            return "handled"

        bus.register(AnalyzeImagesCommand, handler)
        bus.register(QueryDatabaseCommand, handler)

        registered = bus.registered_commands
        assert len(registered) == 2
        assert AnalyzeImagesCommand in registered
        assert QueryDatabaseCommand in registered


class TestCommandBusExecute:
    """Test CommandBus execute method"""

    @pytest.mark.asyncio
    async def test_execute_async_handler(self):
        """Test executing an async command handler"""
        bus = CommandBus()

        async def async_handler(cmd):
            return f"Processed: {cmd.query}"

        bus.register(QueryDatabaseCommand, async_handler)

        command = QueryDatabaseCommand(
            query="test query",
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        result = await bus.execute(command)
        assert result == "Processed: test query"

    @pytest.mark.asyncio
    async def test_execute_sync_handler(self):
        """Test executing a synchronous command handler"""
        bus = CommandBus()

        def sync_handler(cmd):
            return f"Sync: {cmd.query}"

        bus.register(QueryDatabaseCommand, sync_handler)

        command = QueryDatabaseCommand(
            query="sync query",
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        result = await bus.execute(command)
        assert result == "Sync: sync query"

    @pytest.mark.asyncio
    async def test_execute_unregistered_command_raises_error(self):
        """Test that executing an unregistered command raises ValueError"""
        bus = CommandBus()

        command = QueryDatabaseCommand(
            query="test",
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        with pytest.raises(ValueError) as exc_info:
            await bus.execute(command)

        assert "No handler registered" in str(exc_info.value)
        assert "QueryDatabaseCommand" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_handler_exception_propagates(self):
        """Test that exceptions from handlers are propagated"""
        bus = CommandBus()

        async def failing_handler(cmd):
            raise RuntimeError("Handler failed")

        bus.register(QueryDatabaseCommand, failing_handler)

        command = QueryDatabaseCommand(
            query="test",
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        with pytest.raises(RuntimeError) as exc_info:
            await bus.execute(command)

        assert "Handler failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_handler_receives_correct_command(self):
        """Test that handler receives the correct command instance"""
        bus = CommandBus()
        received_command = None

        async def capture_handler(cmd):
            nonlocal received_command
            received_command = cmd
            return "captured"

        bus.register(AnalyzeImagesCommand, capture_handler)

        command = AnalyzeImagesCommand(
            image_one=b"test",
            image_two=None,
            discord_user_id=999,
            discord_message_id=888,
            discord_channel_id=777,
        )

        await bus.execute(command)

        assert received_command is command
        assert received_command.discord_user_id == 999


class TestCommandBusClearHandlers:
    """Test CommandBus clear_handlers method"""

    def test_clear_handlers_removes_all(self):
        """Test that clear_handlers removes all registered handlers"""
        bus = CommandBus()

        def handler(cmd):
            return "handled"

        bus.register(AnalyzeImagesCommand, handler)
        bus.register(QueryDatabaseCommand, handler)

        assert len(bus.handlers) == 2

        bus.clear_handlers()

        assert len(bus.handlers) == 0
        assert bus.registered_commands == []

    def test_clear_handlers_on_empty_bus(self):
        """Test that clear_handlers works on an empty bus"""
        bus = CommandBus()

        bus.clear_handlers()  # Should not raise

        assert len(bus.handlers) == 0
