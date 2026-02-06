import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from http import HTTPStatus
from app.core.settings import settings
from app.services.discord_client import bot
from app.models.schemas import GameStatsResponse
from app.handlers import (
    register_gemini_handlers,
    register_mongodb_handlers,
    register_discord_response_handler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initialising start up configurations.")

    # Register event handlers
    logger.info("Registering event handlers...")
    register_gemini_handlers()
    register_mongodb_handlers()
    register_discord_response_handler()
    logger.info("Event handlers registered successfully.")

    try:
        logger.info("Starting Discord bot...")
        bot_task = asyncio.create_task(bot.start(settings.DISCORD_BOT_TOKEN))
        # Give the bot a moment to start connecting
        await asyncio.sleep(1)
        logger.info("Discord bot task created successfully.")
    except Exception as e:
        logger.error(f"Error starting Discord bot: {str(e)}", exc_info=True)

    yield

    try:
        logger.info("Closing Discord bot...")
        await bot.close()
        logger.info("Discord bot closed successfully.")
    except Exception as e:
        logger.error(f"Error closing Discord bot: {str(e)}", exc_info=True)


app = FastAPI(title="Debfrief API", version="1.0.0", lifespan=lifespan)


@app.get("/")
def health_check():
    return HTTPStatus.OK


@app.post("/schemas/test")
def test_game_stats(game_stats: GameStatsResponse):
    return game_stats
