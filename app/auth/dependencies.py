import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import verify_token

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
	"""Dependency to extract and verify JWT token from request

	Used as a route dependency: @router.get("/protected", dependencies=[Depends(get_current_user)])
	or to get the user ID: async def endpoint(user_id: int = Depends(get_current_user))

	Args:
	    credentials: HTTP Bearer token from Authorization header

	Returns:
	    Discord user ID if token is valid

	Raises:
	    HTTPException 401 if token is missing or invalid
	"""
	token = credentials.credentials

	token_data = verify_token(token)
	if token_data is None:
		logger.warning('Invalid or expired token attempted')
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail='Invalid or expired token',
			headers={'WWW-Authenticate': 'Bearer'},
		)

	return token_data.discord_user_id


async def verify_user_access(
	requested_user_id: int, current_user_id: int = Depends(get_current_user)
) -> bool:
	"""Verify that current user can access another user's data

	Users can only access their own data. This prevents user 123 from
	accessing user 456's match statistics.

	Args:
	    requested_user_id: The user ID being requested
	    current_user_id: The authenticated user making the request

	Returns:
	    True if access is allowed

	Raises:
	    HTTPException 403 if user tries to access another user's data
	"""
	if current_user_id != requested_user_id:
		logger.warning(
			f"User {current_user_id} attempted to access user {requested_user_id}'s data"
		)
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access another user's data"
		)

	return True
