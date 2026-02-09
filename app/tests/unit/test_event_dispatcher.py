import pytest
from app.events import EventDispatcher, GameStatsAnalyzed, MatchSaved
from app.models.schemas import GameStatsResponse
from app.tests.mocks import FakeGeminiClient


class TestEventDispatcherInit:
    """Test EventDispatcher initialization"""

    def test_init_creates_empty_handlers(self):
        """Test that EventDispatcher starts with empty handlers"""
        dispatcher = EventDispatcher()
        assert dispatcher.handlers == {}
        assert dispatcher.registered_events == []


class TestEventDispatcherSubscribe:
    """Test EventDispatcher subscription"""

    def test_subscribe_single_handler(self):
        """Test subscribing a single handler"""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        dispatcher.subscribe(GameStatsAnalyzed, handler)

        assert GameStatsAnalyzed in dispatcher.handlers
        assert len(dispatcher.handlers[GameStatsAnalyzed]) == 1
        assert dispatcher.handlers[GameStatsAnalyzed][0] == handler

    def test_subscribe_multiple_handlers_to_same_event(self):
        """Test subscribing multiple handlers to the same event"""
        dispatcher = EventDispatcher()

        def handler1(event):
            pass

        def handler2(event):
            pass

        dispatcher.subscribe(GameStatsAnalyzed, handler1)
        dispatcher.subscribe(GameStatsAnalyzed, handler2)

        assert len(dispatcher.handlers[GameStatsAnalyzed]) == 2
        assert handler1 in dispatcher.handlers[GameStatsAnalyzed]
        assert handler2 in dispatcher.handlers[GameStatsAnalyzed]

    def test_subscribe_handlers_to_different_events(self):
        """Test subscribing handlers to different events"""
        dispatcher = EventDispatcher()

        def handler1(event):
            pass

        def handler2(event):
            pass

        dispatcher.subscribe(GameStatsAnalyzed, handler1)
        dispatcher.subscribe(MatchSaved, handler2)

        assert len(dispatcher.handlers) == 2
        assert GameStatsAnalyzed in dispatcher.handlers
        assert MatchSaved in dispatcher.handlers

    def test_registered_events_property(self):
        """Test the registered_events property"""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        dispatcher.subscribe(GameStatsAnalyzed, handler)
        dispatcher.subscribe(MatchSaved, handler)

        registered = dispatcher.registered_events
        assert len(registered) == 2
        assert GameStatsAnalyzed in registered
        assert MatchSaved in registered

    def test_registered_handlers_property(self):
        """Test the registered_handlers property"""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        dispatcher.subscribe(GameStatsAnalyzed, handler)

        handlers = dispatcher.registered_handlers
        assert handlers is dispatcher.handlers
        assert GameStatsAnalyzed in handlers


class TestEventDispatcherEmit:
    """Test EventDispatcher emit method"""

    @pytest.mark.asyncio
    async def test_emit_calls_async_handler(self):
        """Test that emit calls async handlers"""
        dispatcher = EventDispatcher()
        called = False

        async def async_handler(event):
            nonlocal called
            called = True

        dispatcher.subscribe(GameStatsAnalyzed, async_handler)

        game_stats = await FakeGeminiClient().generate_game_stats(b"test", b"test")
        event = GameStatsAnalyzed(
            game_stats=game_stats,
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        await dispatcher.emit(event)

        assert called is True

    @pytest.mark.asyncio
    async def test_emit_calls_sync_handler(self):
        """Test that emit calls synchronous handlers"""
        dispatcher = EventDispatcher()
        called = False

        def sync_handler(event):
            nonlocal called
            called = True

        dispatcher.subscribe(GameStatsAnalyzed, sync_handler)

        game_stats = await FakeGeminiClient().generate_game_stats(b"test", b"test")
        event = GameStatsAnalyzed(
            game_stats=game_stats,
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        await dispatcher.emit(event)

        assert called is True

    @pytest.mark.asyncio
    async def test_emit_calls_all_handlers(self):
        """Test that emit calls all registered handlers"""
        dispatcher = EventDispatcher()
        call_count = 0

        async def handler1(event):
            nonlocal call_count
            call_count += 1

        async def handler2(event):
            nonlocal call_count
            call_count += 10

        dispatcher.subscribe(GameStatsAnalyzed, handler1)
        dispatcher.subscribe(GameStatsAnalyzed, handler2)

        game_stats = await FakeGeminiClient().generate_game_stats(b"test", b"test")
        event = GameStatsAnalyzed(
            game_stats=game_stats,
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        await dispatcher.emit(event)

        assert call_count == 11  # 1 + 10

    @pytest.mark.asyncio
    async def test_emit_with_no_handlers_does_nothing(self):
        """Test that emit with no handlers completes without error"""
        dispatcher = EventDispatcher()

        game_stats = await FakeGeminiClient().generate_game_stats(b"test", b"test")
        event = GameStatsAnalyzed(
            game_stats=game_stats,
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        # Should not raise
        await dispatcher.emit(event)

    @pytest.mark.asyncio
    async def test_emit_handler_exception_does_not_stop_others(self):
        """Test that an exception in one handler doesn't stop others"""
        dispatcher = EventDispatcher()
        handler2_called = False

        async def failing_handler(event):
            raise RuntimeError("Handler failed")

        async def handler2(event):
            nonlocal handler2_called
            handler2_called = True

        dispatcher.subscribe(GameStatsAnalyzed, failing_handler)
        dispatcher.subscribe(GameStatsAnalyzed, handler2)

        game_stats = await FakeGeminiClient().generate_game_stats(b"test", b"test")
        event = GameStatsAnalyzed(
            game_stats=game_stats,
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
        )

        # Should not raise, should log the error
        await dispatcher.emit(event)

        # Second handler should still be called
        assert handler2_called is True

    @pytest.mark.asyncio
    async def test_emit_handler_receives_correct_event(self):
        """Test that handlers receive the correct event instance"""
        dispatcher = EventDispatcher()
        received_event = None

        async def capture_handler(event):
            nonlocal received_event
            received_event = event

        dispatcher.subscribe(GameStatsAnalyzed, capture_handler)

        game_stats = await FakeGeminiClient().generate_game_stats(b"test", b"test")
        event = GameStatsAnalyzed(
            game_stats=game_stats,
            discord_user_id=999,
            discord_message_id=888,
            discord_channel_id=777,
        )

        await dispatcher.emit(event)

        assert received_event is event
        assert received_event.discord_user_id == 999


class TestEventDispatcherClearHandlers:
    """Test EventDispatcher clear_handlers method"""

    def test_clear_handlers_removes_all(self):
        """Test that clear_handlers removes all registered handlers"""
        dispatcher = EventDispatcher()

        def handler(event):
            pass

        dispatcher.subscribe(GameStatsAnalyzed, handler)
        dispatcher.subscribe(MatchSaved, handler)

        assert len(dispatcher.handlers) == 2

        dispatcher.clear_handlers()

        assert len(dispatcher.handlers) == 0
        assert dispatcher.registered_events == []

    def test_clear_handlers_on_empty_dispatcher(self):
        """Test that clear_handlers works on an empty dispatcher"""
        dispatcher = EventDispatcher()

        dispatcher.clear_handlers()  # Should not raise

        assert len(dispatcher.handlers) == 0
