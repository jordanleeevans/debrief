import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.auth.routes import router as auth_router
from app.models.schemas import GameStatsResponse
from app.routes import router as matches_router

# Configure logging
logging.basicConfig(
	level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
	title='Debrief API',
	version='1.0.0',
	description='Discord bot for Call of Duty statistics extraction and analysis',
)
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')

# Include routes
app.include_router(auth_router)
app.include_router(matches_router)


@app.get('/')
def health_check():
	"""Health check endpoint"""
	return {'status': 'ok'}


@app.post('/schemas/test')
def test_game_stats(game_stats: GameStatsResponse):
	"""Test endpoint for validating GameStatsResponse schemas"""
	return game_stats
