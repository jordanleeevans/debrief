from datetime import datetime, timedelta, timezone

import jwt
import pytest

pytest.importorskip('pydantic')

from app.shared.auth.jwt import TokenData, create_access_token, verify_token
from app.shared.core.settings import settings


class TestCreateAccessToken:
	"""Tests for JWT token creation"""

	def test_create_access_token_valid(self):
		"""Test creating a valid JWT token"""
		discord_user_id = 123456789
		token = create_access_token(discord_user_id)

		assert isinstance(token, str)
		assert len(token) > 0

	def test_create_access_token_contains_user_id(self):
		"""Test that token contains the Discord user ID"""
		discord_user_id = 987654321
		token = create_access_token(discord_user_id)

		# Decode without verification to check payload
		payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

		assert payload['discord_user_id'] == discord_user_id

	def test_create_access_token_has_expiration(self):
		"""Test that token has expiration claim"""
		token = create_access_token(123456789)

		payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

		assert 'exp' in payload
		assert 'iat' in payload
		assert payload['exp'] > payload['iat']

	def test_create_access_token_expiration_duration(self):
		"""Test that token expires according to JWT_EXPIRATION setting"""
		token = create_access_token(123456789)

		payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

		exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
		iat_time = datetime.fromtimestamp(payload['iat'], tz=timezone.utc)
		duration = (exp_time - iat_time).total_seconds()

		# Allow 1 second tolerance for test execution time
		assert abs(duration - settings.JWT_EXPIRATION) <= 1


class TestVerifyToken:
	"""Tests for JWT token verification"""

	def test_verify_token_valid(self):
		"""Test verifying a valid token"""
		discord_user_id = 123456789
		token = create_access_token(discord_user_id)

		token_data = verify_token(token)

		assert token_data is not None
		assert isinstance(token_data, TokenData)
		assert token_data.discord_user_id == discord_user_id

	def test_verify_token_invalid_signature(self):
		"""Test that token with wrong signature is rejected"""
		discord_user_id = 123456789
		token = create_access_token(discord_user_id)

		# Tamper with token
		tampered_token = token[:-10] + '0000000000'

		token_data = verify_token(tampered_token)
		assert token_data is None

	def test_verify_token_expired(self):
		"""Test that expired token is rejected"""
		# Create a token with very short expiration
		payload = {
			'discord_user_id': 123456789,
			'exp': datetime.now(timezone.utc) - timedelta(seconds=1),
			'iat': datetime.now(timezone.utc) - timedelta(seconds=2),
		}

		expired_token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

		token_data = verify_token(expired_token)
		assert token_data is None

	def test_verify_token_missing_user_id(self):
		"""Test that token without discord_user_id is rejected"""
		payload = {
			'exp': datetime.now(timezone.utc) + timedelta(seconds=3600),
			'iat': datetime.now(timezone.utc),
		}

		invalid_token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

		token_data = verify_token(invalid_token)
		assert token_data is None

	def test_verify_token_invalid_jwt_format(self):
		"""Test that malformed JWT is rejected"""
		invalid_token = 'not.a.valid.jwt.token'

		token_data = verify_token(invalid_token)
		assert token_data is None

	def test_verify_token_empty_string(self):
		"""Test that empty token string is rejected"""
		token_data = verify_token('')
		assert token_data is None


class TestTokenData:
	"""Tests for TokenData class"""

	def test_token_data_initialization(self):
		"""Test TokenData initialization"""
		discord_user_id = 123456789
		token_data = TokenData(discord_user_id=discord_user_id)

		assert token_data.discord_user_id == discord_user_id

	def test_token_data_stores_user_id(self):
		"""Test that TokenData properly stores user ID"""
		user_ids = [111111111, 222222222, 999999999]

		for user_id in user_ids:
			token_data = TokenData(discord_user_id=user_id)
			assert token_data.discord_user_id == user_id
