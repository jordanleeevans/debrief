import pytest
from app.events import EventDispatcher, AnalyzeImagesRequested, FakeEventDispatcher
from app.events.events import GameStatsAnalyzed
from app.services.gemini import FakeGeminiClient


def test_register_gemini_handlers():
    """Test that the Gemini handlers are registered correctly"""
    dispatcher = EventDispatcher()

    from app.handlers.gemini import register_gemini_handlers

    register_gemini_handlers(dispatcher)

    assert len(dispatcher.registered_events) == 1
    assert AnalyzeImagesRequested in dispatcher.registered_events


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

    assert len(dispatcher.emitted_events) == 1

    emitted_event: GameStatsAnalyzed = dispatcher.emitted_events[0]
    assert emitted_event.game_stats == game_stats
    assert emitted_event.discord_user_id == event.discord_user_id
    assert emitted_event.discord_message_id == event.discord_message_id
