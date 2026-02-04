import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from http import HTTPStatus
from app.core.settings import settings
from app.services.discord_client import bot
from app.models.schemas import GameStats

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initialising start up configurations.")
    asyncio.create_task(bot.start(settings.DISCORD_BOT_TOKEN))

    yield
    await bot.close()


app = FastAPI(title="Debfrief API", version="1.0.0", lifespan=lifespan)


@app.get("/")
def health_check():
    return HTTPStatus.OK


@app.post("/schemas/test")
def test_game_stats(game_stats: GameStats):
    return game_stats
