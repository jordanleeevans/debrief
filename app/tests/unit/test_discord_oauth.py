from unittest.mock import AsyncMock, patch

import httpx
import pytest

pytest.importorskip('pydantic')

from app.auth.discord import (
	DISCORD_API_BASE,
	exchange_code_for_token,
	get_discord_oauth_url,
	get_discord_user,
)
from app.core.settings import settings
from app.tests.mocks.oauth import (
	FakeDiscordOAuthResponse,
	FakeDiscordUserResponse,
	create_fake_httpx_client,
)


class TestGetDiscordOAuthUrl:
	"""Tests for Discord OAuth URL generation"""

	def test_get_discord_oauth_url_returns_string(self):
		"""Test that OAuth URL is returned as string"""
		url = get_discord_oauth_url()
		assert isinstance(url, str)

	def test_get_discord_oauth_url_contains_discord_host(self):
		"""Test that URL points to Discord"""
		url = get_discord_oauth_url()
		assert 'discord.com' in url

	def test_get_discord_oauth_url_contains_client_id(self):
		"""Test that URL contains client ID"""
		url = get_discord_oauth_url()
		assert settings.DISCORD_CLIENT_ID in url

	def test_get_discord_oauth_url_contains_redirect_uri(self):
		"""Test that URL contains redirect URI"""
		url = get_discord_oauth_url()
		assert 'redirect_uri=' in url

	def test_get_discord_oauth_url_contains_response_type(self):
		"""Test that URL contains response_type=code"""
		url = get_discord_oauth_url()
		assert 'response_type=code' in url

	def test_get_discord_oauth_url_contains_scope(self):
		"""Test that URL contains identify scope"""
		url = get_discord_oauth_url()
		assert 'scope=identify' in url

	def test_get_discord_oauth_url_has_oauth2_authorize(self):
		"""Test that URL points to OAuth2 authorize endpoint"""
		url = get_discord_oauth_url()
		assert 'oauth2/authorize' in url


class TestExchangeCodeForToken:
	"""Tests for Discord OAuth code exchange"""

	@pytest.mark.asyncio
	async def test_exchange_code_for_token_success(self):
		"""Test successfully exchanging authorization code for token"""
		fake_token = 'fake_access_token_12345'
		fake_response = FakeDiscordOAuthResponse(access_token=fake_token)
		fake_client = create_fake_httpx_client(token_response=fake_response)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			result = await exchange_code_for_token('test_code_12345')

		assert result == fake_token

	@pytest.mark.asyncio
	async def test_exchange_code_for_token_no_access_token(self):
		"""Test that None is returned when response has no access_token"""
		from unittest.mock import MagicMock

		fake_response = FakeDiscordOAuthResponse(access_token='')
		fake_response.json = MagicMock(return_value={'access_token': None})
		fake_client = create_fake_httpx_client(token_response=fake_response)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			result = await exchange_code_for_token('test_code')

		assert result is None

	@pytest.mark.asyncio
	async def test_exchange_code_for_token_http_error(self):
		"""Test that None is returned on HTTP error"""
		error = httpx.HTTPStatusError('Unauthorized', request=None, response=None)
		fake_client = create_fake_httpx_client(token_error=error)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			result = await exchange_code_for_token('invalid_code')

		assert result is None

	@pytest.mark.asyncio
	async def test_exchange_code_for_token_posts_to_correct_endpoint(self):
		"""Test that POST is made to correct Discord endpoint"""
		fake_response = FakeDiscordOAuthResponse(access_token='token123')
		fake_client = AsyncMock()
		fake_client.post = AsyncMock(return_value=fake_response)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			await exchange_code_for_token('test_code')

		fake_client.post.assert_called_once()
		call_args = fake_client.post.call_args
		assert f'{DISCORD_API_BASE}/oauth2/token' in str(call_args)

	@pytest.mark.asyncio
	async def test_exchange_code_for_token_includes_code(self):
		"""Test that authorization code is included in request"""
		test_code = 'specific_auth_code_xyz'
		fake_response = FakeDiscordOAuthResponse(access_token='token123')
		fake_client = AsyncMock()
		fake_client.post = AsyncMock(return_value=fake_response)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			await exchange_code_for_token(test_code)

		call_kwargs = fake_client.post.call_args[1]
		assert 'data' in call_kwargs
		assert call_kwargs['data']['code'] == test_code


class TestGetDiscordUser:
	"""Tests for Discord user information retrieval"""

	@pytest.mark.asyncio
	async def test_get_discord_user_success(self):
		"""Test successfully fetching Discord user information"""
		fake_user_response = FakeDiscordUserResponse(user_id=123456789, username='testuser')
		fake_client = create_fake_httpx_client(user_response=fake_user_response)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			result = await get_discord_user('fake_token_123')

		assert result is not None
		assert result['username'] == 'testuser'
		assert result['id'] == '123456789'

	@pytest.mark.asyncio
	async def test_get_discord_user_http_error(self):
		"""Test that None is returned on HTTP error"""
		error = httpx.HTTPStatusError('Unauthorized', request=None, response=None)
		fake_client = create_fake_httpx_client(user_error=error)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			result = await get_discord_user('invalid_token')

		assert result is None

	@pytest.mark.asyncio
	async def test_get_discord_user_gets_correct_endpoint(self):
		"""Test that GET is made to correct Discord endpoint"""
		fake_user_response = FakeDiscordUserResponse()
		fake_client = AsyncMock()
		fake_client.get = AsyncMock(return_value=fake_user_response)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			await get_discord_user('token123')

		fake_client.get.assert_called_once()
		call_args = fake_client.get.call_args
		assert f'{DISCORD_API_BASE}/users/@me' in str(call_args)

	@pytest.mark.asyncio
	async def test_get_discord_user_includes_token_in_header(self):
		"""Test that access token is included in Authorization header"""
		test_token = 'specific_access_token_abc'
		fake_user_response = FakeDiscordUserResponse()
		fake_client = AsyncMock()
		fake_client.get = AsyncMock(return_value=fake_user_response)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			await get_discord_user(test_token)

		call_kwargs = fake_client.get.call_args[1]
		assert 'headers' in call_kwargs
		assert call_kwargs['headers']['Authorization'] == f'Bearer {test_token}'

	@pytest.mark.asyncio
	async def test_get_discord_user_returns_full_user_data(self):
		"""Test that complete user data is returned"""
		fake_user_response = FakeDiscordUserResponse(
			user_id=999888777, username='anotheruser', avatar='avatar_hash_123'
		)
		fake_client = create_fake_httpx_client(user_response=fake_user_response)

		mock_async_client = AsyncMock()
		mock_async_client.__aenter__.return_value = fake_client
		mock_async_client.__aexit__.return_value = None

		with patch('app.auth.discord.httpx.AsyncClient', return_value=mock_async_client):
			result = await get_discord_user('token123')

		assert result['id'] == '999888777'
		assert result['username'] == 'anotheruser'
		assert result['avatar'] == 'avatar_hash_123'
