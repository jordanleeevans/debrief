import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.events import EventDispatcher
from app.commands import CommandBus
from app.models.schemas import GameStatsResponse
from app.routes import router
from app.utils import (
    setup_handlers,
    start_bot,
    stop_bot,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage bot lifecycle and handler setup"""
    from app.services.discord import bot

    logger.info("Starting application...")

    # Create dispatcher and command bus (only once per startup, not per reload)
    event_dispatcher = EventDispatcher()
    command_bus = CommandBus()

    # Setup command bus and event dispatcher
    bot.command_bus = command_bus
    bot.event_dispatcher = event_dispatcher

    # Register handlers
    setup_handlers(command_bus, event_dispatcher)

    # Start bot
    await start_bot()

    yield

    # Cleanup
    await stop_bot()


# Create FastAPI app
app = FastAPI(
    title="Debrief API",
    version="1.0.0",
    description="Discord bot for Call of Duty statistics extraction and analysis",
    lifespan=lifespan,
)

# Include routes
app.include_router(router)


@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/schemas/test")
def test_game_stats(game_stats: GameStatsResponse):
    """Test endpoint for validating GameStatsResponse schemas"""
    return game_stats
