import logging
from typing import Optional

import httpx

from app.core.settings import settings

logger = logging.getLogger(__name__)

DISCORD_API_BASE = 'https://discord.com/api/v10'


def get_discord_oauth_url() -> str:
	"""Get the Discord OAuth 2.0 authorization URL

	Returns:
	    URL where user should be redirected to authenticate with Discord
	"""
	params = {
		'client_id': settings.DISCORD_CLIENT_ID,
		'redirect_uri': settings.DISCORD_REDIRECT_URI,
		'response_type': 'code',
		'scope': 'identify',  # Only request user ID and username
	}

	query_string = '&'.join(f'{k}={v}' for k, v in params.items())
	url = f'https://discord.com/oauth2/authorize?{query_string}'

	logger.debug('Generated Discord OAuth URL')
	return url


async def exchange_code_for_token(code: str) -> Optional[str]:
	"""Exchange authorization code for access token

	Args:
	    code: Authorization code from Discord redirect

	Returns:
	    Access token string, or None if exchange fails
	"""
	data = {
		'grant_type': 'authorization_code',
		'code': code,
		'redirect_uri': settings.DISCORD_REDIRECT_URI,
		'client_id': settings.DISCORD_CLIENT_ID,
		'client_secret': settings.DISCORD_CLIENT_SECRET,
	}
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}

	try:
		async with httpx.AsyncClient() as client:
			response = await client.post(
				f'{DISCORD_API_BASE}/oauth2/token', data=data, headers=headers
			)
			logger.info(f'Received response from Discord token exchange {response.json()}')
			response.raise_for_status()

			token_data = response.json()
			access_token = token_data.get('access_token')

			if not access_token:
				logger.error('No access token in Discord response')
				return None

			logger.debug('Successfully exchanged code for access token')
			return access_token

	except httpx.HTTPError as e:
		logger.error(f'Failed to exchange code for token: {str(e)}', exc_info=True)
		return None


async def get_discord_user(access_token: str) -> Optional[dict]:
	"""Fetch Discord user information using access token

	Args:
	    access_token: Discord OAuth access token

	Returns:
	    Dict with user info (id, username, avatar, etc.), or None if fetch fails
	"""
	headers = {'Authorization': f'Bearer {access_token}'}

	try:
		async with httpx.AsyncClient() as client:
			response = await client.get(f'{DISCORD_API_BASE}/users/@me', headers=headers)
			response.raise_for_status()

			user_data = response.json()
			logger.info(f'Fetched Discord user: {user_data.get("id")}')
			return user_data

	except httpx.HTTPError as e:
		logger.error(f'Failed to fetch Discord user: {str(e)}', exc_info=True)
		return None
