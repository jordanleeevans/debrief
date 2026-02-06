import pytest
from app.events import EventDispatcher, AnalyzeImagesRequested, FakeEventDispatcher
from app.events.events import GameStatsAnalyzed, MatchSaved
from app.services.gemini import FakeGeminiClient
from app.db.mongo import FakeAsyncDatabase


def test_register_mongodb_handlers():
    """Test that the MongoDB handlers are registered correctly"""
    dispatcher = EventDispatcher()

    from app.handlers.mongodb_handler import register_mongodb_handlers

    register_mongodb_handlers(dispatcher)

    assert len(dispatcher.registered_events) == 1
    assert GameStatsAnalyzed in dispatcher.registered_events


@pytest.mark.asyncio
async def test_handle_game_stats_analyzed_emits_match_saved():
    """Test that the GameStatsAnalyzed handler emits MatchSaved event"""
    from app.handlers.mongodb_handler import handle_match_saved

    game_stats = await FakeGeminiClient().generate_game_stats(b"image1", b"image2")
    dispatcher = FakeEventDispatcher()
    event = GameStatsAnalyzed(
        game_stats=game_stats,
        discord_user_id=123,
        discord_message_id=456,
    )
    db = FakeAsyncDatabase()

    await handle_match_saved(event, dispatcher, db)

    assert len(dispatcher.emitted_events) == 1

    emitted_event: MatchSaved = dispatcher.emitted_events[0]
    assert emitted_event.discord_user_id == event.discord_user_id
    assert emitted_event.discord_message_id == event.discord_message_id
