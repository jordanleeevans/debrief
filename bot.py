"""Discord Bot Entrypoint - runs separately from FastAPI"""

import asyncio
import logging

from app.commands import CommandBus
from app.core.settings import settings
from app.events import EventDispatcher
from app.services.discord import bot
from app.utils import setup_handlers

# Configure logging
logging.basicConfig(
	level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
	"""Start the Discord bot"""
	logger.info('Starting Discord bot...')

	# Create dispatcher and command bus
	event_dispatcher = EventDispatcher()
	command_bus = CommandBus()

	# Setup command bus and event dispatcher
	bot.command_bus = command_bus
	bot.event_dispatcher = event_dispatcher

	# Register handlers
	setup_handlers(command_bus, event_dispatcher)

	# Start bot (this blocks until the bot is stopped)
	async with bot:
		logger.info('Discord bot started successfully.')
		await bot.start(settings.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		logger.info('Bot shutdown requested')
	except Exception as e:
		logger.error(f'Bot crashed: {e}', exc_info=True)
		raise
