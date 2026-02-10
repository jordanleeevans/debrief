"""Mocks for Discord OAuth 2.0 API"""

from typing import Optional

import httpx


class FakeDiscordOAuthResponse:
	"""Mock response from Discord OAuth token endpoint"""

	def __init__(
		self,
		access_token: str = 'fake_discord_token',
		error: Optional[str] = None,
		should_raise: bool = False,
	):
		self.access_token = access_token
		self.error = error
		self.status_code = 200 if not error else 401
		self.should_raise = should_raise

	def json(self) -> dict:
		"""Return JSON response from Discord"""
		if self.error:
			return {'error': self.error}
		return {
			'access_token': self.access_token,
			'token_type': 'Bearer',
			'expires_in': 604800,
			'refresh_token': 'fake_refresh_token',
			'scope': 'identify',
		}

	def raise_for_status(self):
		"""Raise HTTP error if status code indicates error"""
		if self.should_raise or self.status_code >= 400:
			raise httpx.HTTPStatusError('Mock HTTP Error', request=None, response=self)


class FakeDiscordUserResponse:
	"""Mock response from Discord user endpoint"""

	def __init__(
		self,
		user_id: int = 123456789,
		username: str = 'testuser',
		avatar: str = 'avatar_hash',
		should_raise: bool = False,
	):
		self.user_id = user_id
		self.username = username
		self.avatar = avatar
		self.status_code = 200
		self.should_raise = should_raise

	def json(self) -> dict:
		"""Return JSON response from Discord"""
		return {
			'id': str(self.user_id),
			'username': self.username,
			'avatar': self.avatar,
			'discriminator': '0001',
			'public_flags': 0,
			'flags': 0,
			'banner': None,
			'banner_color': None,
			'accent_color': None,
			'locale': 'en-US',
			'mfa_enabled': False,
			'premium_type': 0,
			'email': None,
			'verified': False,
		}

	def raise_for_status(self):
		"""Raise HTTP error if status code indicates error"""
		if self.should_raise or self.status_code >= 400:
			raise httpx.HTTPStatusError('Mock HTTP Error', request=None, response=self)


def create_fake_httpx_client(
	token_response: Optional[FakeDiscordOAuthResponse] = None,
	user_response: Optional[FakeDiscordUserResponse] = None,
	token_error: Optional[Exception] = None,
	user_error: Optional[Exception] = None,
):
	"""Create a fake httpx.AsyncClient for testing Discord OAuth flow

	Args:
	    token_response: Response to return from token endpoint (oauth2/token)
	    user_response: Response to return from user endpoint (users/@me)
	    token_error: Exception to raise from token endpoint
	    user_error: Exception to raise from user endpoint

	Returns:
	    Mock configured as fake httpx.AsyncClient
	"""
	from unittest.mock import AsyncMock

	if token_response is None:
		token_response = FakeDiscordOAuthResponse()
	if user_response is None:
		user_response = FakeDiscordUserResponse()

	fake_client = AsyncMock()

	# Configure token endpoint
	if token_error:
		if isinstance(token_error, httpx.HTTPError):
			token_response_with_error = FakeDiscordOAuthResponse(should_raise=True)
			fake_client.post = AsyncMock(return_value=token_response_with_error)
		else:
			fake_client.post = AsyncMock(side_effect=token_error)
	else:
		fake_client.post = AsyncMock(return_value=token_response)

	# Configure user endpoint
	if user_error:
		if isinstance(user_error, httpx.HTTPError):
			user_response_with_error = FakeDiscordUserResponse(should_raise=True)
			fake_client.get = AsyncMock(return_value=user_response_with_error)
		else:
			fake_client.get = AsyncMock(side_effect=user_error)
	else:
		fake_client.get = AsyncMock(return_value=user_response)

	return fake_client
