import json
import pytest
from tests.integration.test_discord_lifespan import FakeBot
from app.services.gemini import FakeGeminiClient

def test_get_channel_from_cache_returns_none_for_missing_channel():
    """Test that get_channel_from_cache returns None when channel is not in cache"""
    from app.handlers.discord_response_handler import get_channel_from_cache

    bot = FakeBot()
    channel = get_channel_from_cache(bot, 123)
    assert channel is None

def test_get_channel_from_cache_returns_channel():
    """Test that get_channel_from_cache returns the channel when it is in cache"""
    from app.handlers.discord_response_handler import get_channel_from_cache

    bot = FakeBot()
    fake_channel = object()  # Use a simple object as a fake channel
    bot.cached_channels[123] = fake_channel

    channel = get_channel_from_cache(bot, 123)
    assert channel == fake_channel

@pytest.mark.asyncio
async def test_fetch_channel_from_api_returns_channel(monkeypatch):
    """Test that fetch_channel_from_api returns a channel and caches it"""
    from app.handlers.discord_response_handler import fetch_channel_from_api

    bot = FakeBot()

    # Simulate fetching a channel from the API
    channel = await fetch_channel_from_api(bot, 123)
    assert channel is not None
    assert bot.cached_channels[123] == channel

@pytest.mark.asyncio
async def test_fetch_channel_from_api_handles_exception(monkeypatch):
    """Test that fetch_channel_from_api returns None and logs an error when an exception occurs"""
    from app.handlers.discord_response_handler import fetch_channel_from_api

    bot = FakeBot()

    # Simulate an exception when fetching the channel
    async def mock_fetch_channel(channel_id):
        raise Exception("API error")
    
    monkeypatch.setattr(bot, "fetch_channel", mock_fetch_channel)

    channel = await fetch_channel_from_api(bot, 123)
    assert channel is None

@pytest.mark.asyncio
async def test_handle_discord_response_sends_message():
    """Test that handle_discord_response sends a message to the correct channel"""
    from app.handlers.discord_response_handler import handle_discord_response
    from app.events import MatchSaved
    class FakeChannel:
        def __init__(self):
            self.sent_messages = []
        
        async def send(self, content):
            self.sent_messages.append(content)

    bot = FakeBot()
    fake_channel = FakeChannel()
    bot.cached_channels[123] = fake_channel
    game_stats = await FakeGeminiClient().generate_game_stats(b"image1", b"image2")

    event = MatchSaved(
        match_id="test_match",
        game_stats=game_stats,
        discord_user_id=456,
        discord_message_id=789,
        discord_channel_id=123,
    )

    await handle_discord_response(bot, event)
    assert len(fake_channel.sent_messages) == 1
    assert json.loads(fake_channel.sent_messages[0].split("```json\n")[1].split("\n```")[0]) == event.game_stats.model_dump()

@pytest.mark.asyncio
async def test_handle_discord_response_channel_not_found():
    """Test that handle_discord_response logs an error when the channel cannot be found"""
    from app.handlers.discord_response_handler import handle_discord_response
    from app.events import MatchSaved

    bot = FakeBot()

    game_stats = await FakeGeminiClient().generate_game_stats(b"image1", b"image2")
    event = MatchSaved(
        match_id="test_match",
        game_stats=game_stats,
        discord_user_id=456,
        discord_message_id=789,
        discord_channel_id=123,
    )

    await handle_discord_response(bot, event)
    # Since the channel is not found, we expect an error log but no exceptions raised

def test_register_discord_response_handler():
    """Test that register_discord_response_handler subscribes the handler to the dispatcher"""
    from app.handlers.discord_response_handler import register_discord_response_handler
    from app.events import EventDispatcher, MatchSaved

    dispatcher = EventDispatcher()
    bot = FakeBot()

    register_discord_response_handler(dispatcher, bot)

    # Check that the dispatcher has a subscriber for MatchSaved events
    assert dispatcher.registered_events == [MatchSaved]