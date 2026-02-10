import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from app.core.settings import settings

logger = logging.getLogger(__name__)


class TokenData:
	"""Data stored in JWT token"""

	def __init__(self, discord_user_id: int):
		self.discord_user_id = discord_user_id


def create_access_token(discord_user_id: int) -> str:
	"""Create a JWT access token for a Discord user

	Args:
	    discord_user_id: The Discord user ID to encode in the token

	Returns:
	    JWT token string
	"""
	payload = {
		'discord_user_id': discord_user_id,
		'exp': datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXPIRATION),
		'iat': datetime.now(timezone.utc),
	}

	token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

	logger.info(f'Created JWT token for user {discord_user_id}')
	return token


def verify_token(token: str) -> Optional[TokenData]:
	"""Verify and decode a JWT token

	Args:
	    token: JWT token string to verify

	Returns:
	    TokenData if valid, None if invalid or expired
	"""
	try:
		payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
		discord_user_id = payload.get('discord_user_id')

		if discord_user_id is None:
			logger.warning('Token missing discord_user_id claim')
			return None

		return TokenData(discord_user_id=discord_user_id)

	except jwt.ExpiredSignatureError:
		logger.warning('Token has expired')
		return None
	except jwt.InvalidTokenError as e:
		logger.warning(f'Invalid token: {str(e)}')
		return None
	except Exception as e:
		logger.error(f'Error verifying token: {str(e)}', exc_info=True)
		return None
