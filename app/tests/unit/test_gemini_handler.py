import pytest
from app.events import AnalyzeImagesRequested
from app.events.events import GameStatsAnalyzed, GeminiQueryRequest, QueryGenerated, AnalyzeImagesRequested
from app.tests.mocks import FakeGeminiClient, FakeEventDispatcher


def test_register_gemini_handlers():
    """Test that the Gemini handlers are registered correctly"""
    dispatcher = FakeEventDispatcher()

    from app.handlers.gemini import register_gemini_handlers

    register_gemini_handlers(dispatcher)

    dispatched_events_set = set(dispatcher.registered_events)
    expected_events_set = set((GeminiQueryRequest, AnalyzeImagesRequested))

    assert dispatched_events_set == expected_events_set


@pytest.mark.asyncio
async def test_handle_analyze_images_emits_game_stats_analyzed():
    """Test that the analyze images handler emits GameStatsAnalyzed event"""
    from app.handlers.gemini import handle_analyze_images

    dispatcher = FakeEventDispatcher()
    client = FakeGeminiClient()
    event = AnalyzeImagesRequested(
        image_one="image1.png",
        image_two="image2.png",
        discord_user_id=123,
        discord_message_id=456,
        discord_channel_id=789,
    )

    game_stats = await client.generate_game_stats(event.image_one, event.image_two)

    await handle_analyze_images(event, dispatcher, client)

    emitted_event: GameStatsAnalyzed = next(event for event in dispatcher.emitted_events if isinstance(event, GameStatsAnalyzed))
    assert emitted_event.game_stats == game_stats
    assert emitted_event.discord_user_id == event.discord_user_id
    assert emitted_event.discord_message_id == event.discord_message_id

@pytest.mark.asyncio
async def test_handle_gemini_query_emits_query_generated():
    
    from app.handlers.gemini import handle_gemini_query

    dispatcher = FakeEventDispatcher()
    client = FakeGeminiClient()
    event = QueryGenerated(
        query="query",
        response="response",
        discord_user_id=123,
        discord_message_id=456,
        discord_channel_id=789
    )

    await handle_gemini_query(event, dispatcher, client)

    emitted_event: QueryGenerated = next(event for event in dispatcher.emitted_events if isinstance(event, QueryGenerated))
    assert emitted_event.query == event.query
    assert emitted_event.discord_user_id == event.discord_user_id
    assert emitted_event.discord_message_id == event.discord_message_id
    assert emitted_event.discord_channel_id == event.discord_channel_id