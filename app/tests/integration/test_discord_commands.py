import pytest

# Skip if discord isn't installed in the test environment
pytest.importorskip("discord")

from app.events.events import AnalyzeImagesRequested, GeminiQueryRequest
import app.services.discord as dc
from app.tests.mocks import FakeAttachment, FakeCtx


@pytest.mark.asyncio
async def test_ping_sends_pong(fake_ctx: FakeCtx):
    cmd = dc.bot.get_command("ping")
    assert cmd is not None

    await dc.ping(fake_ctx)
    assert any("Pong" in m for m in fake_ctx.sent)


@pytest.mark.asyncio
async def test_stats_no_attachments(fake_ctx: FakeCtx):
    await dc.stats(fake_ctx)
    assert any("Please attach at least one image" in m for m in fake_ctx.sent)
    assert fake_ctx.bot.dispatcher.emitted_events == []


@pytest.mark.asyncio
async def test_stats_too_large_attachment(fake_ctx: FakeCtx):
    fake_ctx.message.attachments = [FakeAttachment(b"fake image data", size=11_000_000)]
    await dc.stats(fake_ctx)
    assert any("Please attach images smaller than 10MB" in m for m in fake_ctx.sent)
    assert fake_ctx.bot.dispatcher.emitted_events == []


@pytest.mark.asyncio
async def test_stats_too_many_attachments(fake_ctx: FakeCtx):
    fake_ctx.message.attachments = [
        FakeAttachment(b"fake image data 1"),
        FakeAttachment(b"fake image data 2"),
        FakeAttachment(b"fake image data 3"),
    ]
    await dc.stats(fake_ctx)
    assert any("Please attach no more than two images" in m for m in fake_ctx.sent)
    assert fake_ctx.bot.dispatcher.emitted_events == []


@pytest.mark.asyncio
async def test_stats_valid_attachments(fake_ctx: FakeCtx):
    fake_ctx.message.attachments = [
        FakeAttachment(b"fake image data 1"),
        FakeAttachment(b"fake image data 2"),
    ]
    await dc.stats(fake_ctx)

    emitted_events = fake_ctx.bot.dispatcher.emitted_events

    assert len(emitted_events) == 1
    assert isinstance(emitted_events[0], AnalyzeImagesRequested)


@pytest.mark.asyncio
async def test_stats_one_valid_attachment(fake_ctx: FakeCtx):
    fake_ctx.message.attachments = [
        FakeAttachment(b"fake image data 1"),
    ]
    await dc.stats(fake_ctx)
    assert not any("Please attach" in m for m in fake_ctx.sent)

    emitted_events = fake_ctx.bot.dispatcher.emitted_events

    assert len(emitted_events) == 1
    assert isinstance(emitted_events[0], AnalyzeImagesRequested)


@pytest.mark.asyncio
async def test_stats_mixed_valid_and_invalid_attachments(fake_ctx: FakeCtx):
    fake_ctx.message.attachments = [
        FakeAttachment(b"fake image data 1"),
        FakeAttachment(b"fake image data 2", size=11_000_000),  # Invalid due to size
    ]
    await dc.stats(fake_ctx)
    assert any("Please attach images smaller than 10MB" in m for m in fake_ctx.sent)
    assert fake_ctx.bot.dispatcher.emitted_events == []


@pytest.mark.asyncio
async def test_query_no_input(fake_ctx: FakeCtx):
    await dc.query(fake_ctx)
    assert fake_ctx.bot.dispatcher.emitted_events == []


@pytest.mark.asyncio
async def test_query_with_input(fake_ctx: FakeCtx):
    fake_ctx.message.content = "!query What is the meaning of life?"
    await dc.query(fake_ctx)
    emitted_events = fake_ctx.bot.dispatcher.emitted_events

    assert len(emitted_events) == 1
    assert isinstance(emitted_events[0], GeminiQueryRequest)
