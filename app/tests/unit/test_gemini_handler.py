import pytest
from app.bot.commands import AnalyzeImagesCommand, QueryDatabaseCommand
from app.bot.events.events import GameStatsAnalyzed, QueryExecuted
from app.tests.mocks import FakeGeminiClient, FakeEventDispatcher


def test_register_gemini_command_handlers():
    """Test that the Gemini command handlers are registered correctly"""
    from app.bot.handlers.gemini import register_gemini_command_handlers
    from app.bot.commands import CommandBus

    dispatcher = FakeEventDispatcher()
    command_bus = CommandBus()

    register_gemini_command_handlers(command_bus, dispatcher)

    registered_commands = set(command_bus.registered_commands)
    expected_commands = set((AnalyzeImagesCommand, QueryDatabaseCommand))

    assert registered_commands == expected_commands


@pytest.mark.asyncio
async def test_handle_analyze_images_command_emits_game_stats_analyzed():
    """Test that the analyze images command handler emits GameStatsAnalyzed event"""
    from app.bot.handlers.gemini import handle_analyze_images_command

    dispatcher = FakeEventDispatcher()
    client = FakeGeminiClient
    command = AnalyzeImagesCommand(
        image_one=b"image1.png",
        image_two=b"image2.png",
        discord_user_id=123,
        discord_message_id=456,
        discord_channel_id=789,
    )

    await handle_analyze_images_command(command, dispatcher, client)

    emitted_event: GameStatsAnalyzed = next(
        event
        for event in dispatcher.emitted_events
        if isinstance(event, GameStatsAnalyzed)
    )
    assert emitted_event.discord_user_id == command.discord_user_id
    assert emitted_event.discord_message_id == command.discord_message_id


@pytest.mark.asyncio
async def test_handle_query_database_command_emits_query_executed():
    """Test that the query database command handler emits QueryExecuted event"""
    from app.bot.handlers.gemini import handle_query_database_command
    from app.tests.mocks import FakeMatchRepository

    dispatcher = FakeEventDispatcher()
    client = FakeGeminiClient
    repository = FakeMatchRepository()
    command = QueryDatabaseCommand(
        query="What are my stats?",
        discord_user_id=123,
        discord_message_id=456,
        discord_channel_id=789,
    )

    await handle_query_database_command(command, dispatcher, client, repository)

    emitted_event: QueryExecuted = next(
        event for event in dispatcher.emitted_events if isinstance(event, QueryExecuted)
    )
    assert emitted_event.query == command.query
    assert emitted_event.discord_user_id == command.discord_user_id
    assert emitted_event.discord_message_id == command.discord_message_id
    assert emitted_event.discord_channel_id == command.discord_channel_id
