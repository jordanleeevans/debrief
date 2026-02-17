import pytest
from app.bot.events import EventDispatcher
from app.bot.events.events import GameStatsAnalyzed, MatchSaved
from app.tests.mocks import (
    FakeMatchRepository,
    FakeGeminiClient,
    FakeEventDispatcher,
)


def test_register_mongodb_event_handlers():
    """Test that the MongoDB event handlers are registered correctly"""
    dispatcher = EventDispatcher()

    from app.bot.handlers.db import register_mongodb_event_handlers

    register_mongodb_event_handlers(dispatcher)

    expected_events = set((GameStatsAnalyzed,))
    registered_events = set(dispatcher.registered_events)

    assert len(dispatcher.registered_events) == len(expected_events)
    assert expected_events == registered_events


@pytest.mark.asyncio
async def test_handle_game_stats_analyzed_emits_match_saved():
    """Test that the GameStatsAnalyzed handler emits MatchSaved event"""
    from app.bot.handlers.db import handle_game_stats_analyzed

    game_stats = await FakeGeminiClient().generate_game_stats(b"image1", b"image2")
    dispatcher = FakeEventDispatcher()
    event = GameStatsAnalyzed(
        game_stats=game_stats,
        discord_user_id=123,
        discord_message_id=456,
        discord_channel_id=789,
    )
    fake_match_repo = FakeMatchRepository()

    await handle_game_stats_analyzed(event, dispatcher, fake_match_repo)

    assert len(dispatcher.emitted_events) == 1

    emitted_event: MatchSaved = dispatcher.emitted_events[0]
    assert emitted_event.discord_user_id == event.discord_user_id
    assert emitted_event.discord_message_id == event.discord_message_id


@pytest.mark.asyncio
async def test_handle_game_stats_analyzed_saves_to_repository():
    """Test that the GameStatsAnalyzed handler saves match data to the repository"""
    from app.bot.handlers.db import handle_game_stats_analyzed

    game_stats = await FakeGeminiClient().generate_game_stats(b"image1", b"image2")
    dispatcher = FakeEventDispatcher()
    event = GameStatsAnalyzed(
        game_stats=game_stats,
        discord_user_id=123,
        discord_message_id=456,
        discord_channel_id=789,
    )
    fake_match_repo = FakeMatchRepository()

    await handle_game_stats_analyzed(event, dispatcher, fake_match_repo)

    assert len(fake_match_repo.matches) == 1
    saved_match = fake_match_repo.matches[0]
    assert saved_match["discord_user_id"] == event.discord_user_id
    assert saved_match["discord_message_id"] == event.discord_message_id
