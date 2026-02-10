import logging
from unittest.mock import patch

import pytest

pytest.importorskip('fastapi')

from app.tests.mocks import FakeBot

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function', autouse=True)
def mock_bot_for_integration_tests():
	"""Mock Discord bot for integration tests to prevent actual bot startup

	This fixture automatically runs for all tests in the integration directory.
	"""
	logger.info('Setting up mock Discord bot for integration test')

	fake_bot = FakeBot()

	# Import the real module to get command functions
	import app.services.discord as dc

	# Register the commands on the fake bot
	fake_bot.add_command('ping', dc.ping)
	fake_bot.add_command('stats', dc.stats)
	fake_bot.add_command('query', dc.query)

	# Mock the bot module
	with patch('app.services.discord.bot', fake_bot):
		logger.info('Discord bot mocked - test will run without connecting to Discord')
		yield fake_bot
