from http import HTTPStatus
from unittest.mock import patch

import pytest

pytest.importorskip('fastapi')

from fastapi.testclient import TestClient

from app.api.main import app


class TestDiscordOAuthEndpoint:
	"""Integration tests for GET /api/auth/discord"""

	def test_get_discord_login_url_returns_200(self):
		"""Test that endpoint returns 200 status"""
		with TestClient(app) as client:
			response = client.get('/api/auth/discord')
			assert response.status_code == HTTPStatus.OK

	def test_get_discord_login_url_returns_auth_url(self):
		"""Test that endpoint returns auth_url field"""
		with TestClient(app) as client:
			response = client.get('/api/auth/discord')
			data = response.json()

			assert 'auth_url' in data
			assert isinstance(data['auth_url'], str)

	def test_get_discord_login_url_contains_discord_authorize(self):
		"""Test that returned URL is valid Discord OAuth URL"""
		with TestClient(app) as client:
			response = client.get('/api/auth/discord')
			data = response.json()
			auth_url = data['auth_url']

			assert 'discord.com/oauth2/authorize' in auth_url
			assert 'client_id=' in auth_url
			assert 'response_type=code' in auth_url


class TestDiscordOAuthCallbackEndpoint:
	"""Integration tests for GET /api/auth/discord/callback"""

	def test_discord_callback_missing_code_returns_422(self):
		"""Test that missing code parameter returns validation error"""
		with TestClient(app) as client:
			response = client.get('/api/auth/discord/callback')
			assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	@patch('app.shared.auth.routes.exchange_code_for_token')
	@patch('app.shared.auth.routes.get_discord_user')
	def test_discord_callback_success(self, mock_get_user, mock_exchange_code):
		"""Test successful OAuth flow through callback"""

		async def async_exchange(*args, **kwargs):
			return 'fake_discord_token'

		async def async_get_user(*args, **kwargs):
			return {'id': '123456789', 'username': 'testuser'}

		mock_exchange_code.side_effect = async_exchange
		mock_get_user.side_effect = async_get_user

		with TestClient(app) as client:
			response = client.get('/api/auth/discord/callback?code=test_code_123')

		assert response.status_code == HTTPStatus.OK
		assert 'text/html' in response.headers.get('content-type', '')

	@patch('app.shared.auth.routes.exchange_code_for_token')
	def test_discord_callback_code_exchange_failure(self, mock_exchange_code):
		"""Test that callback returns 400 when code exchange fails"""

		async def async_exchange(*args, **kwargs):
			return None

		mock_exchange_code.side_effect = async_exchange

		with TestClient(app) as client:
			response = client.get('/api/auth/discord/callback?code=invalid_code')

		assert response.status_code == HTTPStatus.BAD_REQUEST

	@patch('app.shared.auth.routes.exchange_code_for_token')
	@patch('app.shared.auth.routes.get_discord_user')
	def test_discord_callback_user_fetch_failure(self, mock_get_user, mock_exchange_code):
		"""Test that callback returns 400 when user fetch fails"""

		async def async_exchange(*args, **kwargs):
			return 'valid_token'

		async def async_get_user(*args, **kwargs):
			return None

		mock_exchange_code.side_effect = async_exchange
		mock_get_user.side_effect = async_get_user

		with TestClient(app) as client:
			response = client.get('/api/auth/discord/callback?code=test_code')

		assert response.status_code == HTTPStatus.BAD_REQUEST

	@patch('app.shared.auth.routes.exchange_code_for_token')
	@patch('app.shared.auth.routes.get_discord_user')
	def test_discord_callback_invalid_user_id(self, mock_get_user, mock_exchange_code):
		"""Test that callback returns 400 when user ID is missing"""

		async def async_exchange(*args, **kwargs):
			return 'valid_token'

		async def async_get_user(*args, **kwargs):
			return {'username': 'testuser'}  # Missing id

		mock_exchange_code.side_effect = async_exchange
		mock_get_user.side_effect = async_get_user

		with TestClient(app) as client:
			response = client.get('/api/auth/discord/callback?code=test_code')

		assert response.status_code == HTTPStatus.BAD_REQUEST

	@patch('app.shared.auth.routes.exchange_code_for_token')
	@patch('app.shared.auth.routes.get_discord_user')
	def test_discord_callback_returns_html_page(self, mock_get_user, mock_exchange_code):
		"""Test that callback returns HTML page with token"""

		async def async_exchange(*args, **kwargs):
			return 'fake_discord_token'

		async def async_get_user(*args, **kwargs):
			return {'id': '123456789', 'username': 'testuser'}

		mock_exchange_code.side_effect = async_exchange
		mock_get_user.side_effect = async_get_user

		with TestClient(app) as client:
			response = client.get('/api/auth/discord/callback?code=test_code')

		assert response.status_code == HTTPStatus.OK
		assert 'text/html' in response.headers.get('content-type', '')


class TestAuthEndpointsRequireNoAuth:
	"""Tests verifying OAuth endpoints don't require existing auth"""

	def test_get_discord_url_no_auth_required(self):
		"""Test that /api/auth/discord doesn't require authentication"""
		with TestClient(app) as client:
			response = client.get('/api/auth/discord')
			assert response.status_code == HTTPStatus.OK

	def test_discord_callback_no_auth_required(self):
		"""Test that /api/auth/discord/callback doesn't require authentication"""
		with TestClient(app) as client:
			response = client.get('/api/auth/discord/callback?code=invalid')
			# Should not return 401 Unauthorized (will be 400 Bad Request due to invalid code)
			assert response.status_code != HTTPStatus.UNAUTHORIZED
