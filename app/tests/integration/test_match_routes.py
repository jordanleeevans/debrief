from http import HTTPStatus

import pytest

pytest.importorskip('fastapi')

from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token
from app.main import app
from app.routes import get_match_repository
from app.tests.mocks import FakeMatchRepository


class TestMatchesEndpointsAuthentication:
	"""Tests verifying match endpoints require authentication"""

	def test_list_matches_without_auth_returns_401(self):
		"""Test that /api/matches requires authentication"""
		with TestClient(app) as client:
			response = client.get('/api/matches')
			assert response.status_code == HTTPStatus.UNAUTHORIZED

	def test_list_matches_with_invalid_token_returns_401(self):
		"""Test that invalid token is rejected"""
		with TestClient(app) as client:
			headers = {'Authorization': 'Bearer invalid_token'}
			response = client.get('/api/matches', headers=headers)
			assert response.status_code == HTTPStatus.UNAUTHORIZED

	def test_list_matches_with_expired_token_returns_401(self):
		"""Test that expired token is rejected"""
		from datetime import datetime, timedelta, timezone

		import jwt

		from app.core.settings import settings

		expired_payload = {
			'discord_user_id': 123456789,
			'exp': datetime.now(timezone.utc) - timedelta(seconds=1),
			'iat': datetime.now(timezone.utc) - timedelta(seconds=100),
		}
		expired_token = jwt.encode(
			expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
		)

		with TestClient(app) as client:
			headers = {'Authorization': f'Bearer {expired_token}'}
			response = client.get('/api/matches', headers=headers)
			assert response.status_code == HTTPStatus.UNAUTHORIZED

	def test_list_matches_with_valid_token_succeeds(self):
		"""Test that valid token grants access"""
		fake_repo = FakeMatchRepository(initial_matches=[])
		token = create_access_token(123456789)

		app.dependency_overrides[get_match_repository] = lambda: fake_repo
		try:
			with TestClient(app) as client:
				headers = {'Authorization': f'Bearer {token}'}
				response = client.get('/api/matches', headers=headers)

			assert response.status_code == HTTPStatus.OK
		finally:
			app.dependency_overrides.clear()


class TestMatchesEndpointsFilterByUser:
	"""Tests verifying matches are filtered by authenticated user"""

	def test_list_matches_filters_by_current_user_id(self):
		"""Test that matches are filtered by current user ID"""
		# Create fake repository with test data
		test_matches = [
			{'_id': '1', 'discord_user_id': 123456789, 'game_mode': 'hardpoint'},
			{'_id': '2', 'discord_user_id': 987654321, 'game_mode': 'search'},
			{'_id': '3', 'discord_user_id': 123456789, 'game_mode': 'control'},
		]
		fake_repo = FakeMatchRepository(initial_matches=test_matches)

		user_id = 123456789
		token = create_access_token(user_id)

		app.dependency_overrides[get_match_repository] = lambda: fake_repo
		try:
			with TestClient(app) as client:
				headers = {'Authorization': f'Bearer {token}'}
				response = client.get('/api/matches?limit=10&skip=0', headers=headers)

			assert response.status_code == HTTPStatus.OK
			data = response.json()
			# Should only return matches for user 123456789
			assert data['count'] == 2
			assert all(m['discord_user_id'] == user_id for m in data['matches'])
		finally:
			app.dependency_overrides.clear()

	def test_list_matches_includes_pagination_stages(self):
		"""Test that pagination works correctly"""
		# Create fake repository with test data
		test_matches = [
			{'_id': f'{i}', 'discord_user_id': 123456789, 'game_mode': 'hardpoint'}
			for i in range(10)
		]
		fake_repo = FakeMatchRepository(initial_matches=test_matches)

		token = create_access_token(123456789)

		app.dependency_overrides[get_match_repository] = lambda: fake_repo
		try:
			with TestClient(app) as client:
				headers = {'Authorization': f'Bearer {token}'}
				response = client.get('/api/matches?limit=3&skip=2', headers=headers)

			data = response.json()
			# Should skip 2 and return 3
			assert data['count'] == 3
			assert data['skip'] == 2
			assert data['limit'] == 3
			assert len(data['matches']) == 3
			# Verify we got matches starting from index 2
			assert data['matches'][0]['_id'] == '2'
		finally:
			app.dependency_overrides.clear()

	def test_list_matches_returns_filtered_results(self):
		"""Test that endpoint returns matches from repository"""
		test_matches = [
			{'_id': '1', 'discord_user_id': 123456789, 'game_mode': 'hardpoint'},
			{'_id': '2', 'discord_user_id': 123456789, 'game_mode': 'search'},
		]
		fake_repo = FakeMatchRepository(initial_matches=test_matches)

		user_id = 123456789
		token = create_access_token(user_id)

		app.dependency_overrides[get_match_repository] = lambda: fake_repo
		try:
			with TestClient(app) as client:
				headers = {'Authorization': f'Bearer {token}'}
				response = client.get('/api/matches', headers=headers)

			assert response.status_code == HTTPStatus.OK
			data = response.json()
			assert 'matches' in data
			assert data['count'] == 2
			assert len(data['matches']) == 2
		finally:
			app.dependency_overrides.clear()

	def test_list_matches_returns_serialized_data(self):
		"""Test that MongoDB ObjectId is serialized to string"""
		from bson import ObjectId

		mongo_id = ObjectId()
		test_matches = [{'_id': mongo_id, 'discord_user_id': 123456789, 'game_mode': 'hardpoint'}]
		fake_repo = FakeMatchRepository(initial_matches=test_matches)

		token = create_access_token(123456789)

		app.dependency_overrides[get_match_repository] = lambda: fake_repo
		try:
			with TestClient(app) as client:
				headers = {'Authorization': f'Bearer {token}'}
				response = client.get('/api/matches', headers=headers)

			data = response.json()
			# ObjectId should be converted to string
			assert isinstance(data['matches'][0]['_id'], str)
			assert data['matches'][0]['_id'] == str(mongo_id)
		finally:
			app.dependency_overrides.clear()

	def test_list_matches_user_isolation(self):
		"""Test that users can only see their own matches"""
		test_matches = [
			{'_id': '1', 'discord_user_id': 111111111, 'game_mode': 'hardpoint'},
			{'_id': '2', 'discord_user_id': 222222222, 'game_mode': 'search'},
			{'_id': '3', 'discord_user_id': 111111111, 'game_mode': 'control'},
		]
		fake_repo = FakeMatchRepository(initial_matches=test_matches)

		user1_token = create_access_token(111111111)

		app.dependency_overrides[get_match_repository] = lambda: fake_repo
		try:
			with TestClient(app) as client:
				headers = {'Authorization': f'Bearer {user1_token}'}
				response = client.get('/api/matches', headers=headers)

			data = response.json()
			# User 111111111 should only see their 2 matches
			assert data['count'] == 2
			assert all(m['discord_user_id'] == 111111111 for m in data['matches'])
			# Should not see user 222222222's match
			assert not any(m['discord_user_id'] == 222222222 for m in data['matches'])
		finally:
			app.dependency_overrides.clear()


class TestMatchesEndpointsValidation:
	"""Tests for query parameter validation"""

	def test_list_matches_limit_must_be_ge_1(self):
		"""Test that limit must be >= 1"""
		token = create_access_token(123456789)

		with TestClient(app) as client:
			headers = {'Authorization': f'Bearer {token}'}
			response = client.get('/api/matches?limit=0', headers=headers)
			assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	def test_list_matches_limit_must_be_le_100(self):
		"""Test that limit must be <= 100"""
		token = create_access_token(123456789)

		with TestClient(app) as client:
			headers = {'Authorization': f'Bearer {token}'}
			response = client.get('/api/matches?limit=101', headers=headers)
			assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	def test_list_matches_skip_must_be_ge_0(self):
		"""Test that skip must be >= 0"""
		token = create_access_token(123456789)

		with TestClient(app) as client:
			headers = {'Authorization': f'Bearer {token}'}
			response = client.get('/api/matches?skip=-1', headers=headers)
			assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	def test_list_matches_default_pagination(self):
		"""Test default pagination values"""
		test_matches = [
			{'_id': f'{i}', 'discord_user_id': 123456789, 'game_mode': 'hardpoint'}
			for i in range(15)
		]
		fake_repo = FakeMatchRepository(initial_matches=test_matches)

		token = create_access_token(123456789)

		app.dependency_overrides[get_match_repository] = lambda: fake_repo
		try:
			with TestClient(app) as client:
				headers = {'Authorization': f'Bearer {token}'}
				response = client.get('/api/matches', headers=headers)

			data = response.json()
			# Default limit=10, skip=0
			assert data['skip'] == 0
			assert data['limit'] == 10
			assert data['count'] == 10  # Should only return 10 out of 15
		finally:
			app.dependency_overrides.clear()


class TestMatchesEndpointsErrorHandling:
	"""Tests for error handling in match endpoints"""

	def test_list_matches_handles_repository_error(self):
		"""Test that repository errors are handled gracefully"""
		fake_repo = FakeMatchRepository()

		# Override list_by_user to raise an exception
		async def error_list(*args, **kwargs):
			raise Exception('Database connection failed')

		fake_repo.list_by_user = error_list

		token = create_access_token(123456789)

		app.dependency_overrides[get_match_repository] = lambda: fake_repo
		try:
			with TestClient(app) as client:
				headers = {'Authorization': f'Bearer {token}'}
				response = client.get('/api/matches', headers=headers)

			assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
		finally:
			app.dependency_overrides.clear()
