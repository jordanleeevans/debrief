import logging

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.auth.discord import exchange_code_for_token, get_discord_oauth_url, get_discord_user
from app.auth.jwt import create_access_token

# Set up Jinja2 templates
templates = Jinja2Templates(directory='app/templates')

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/auth', tags=['auth'])


class AuthResponse(BaseModel):
	"""Response containing JWT access token"""

	access_token: str
	token_type: str = 'bearer'


class AuthUrlResponse(BaseModel):
	"""Response containing Discord OAuth URL"""

	auth_url: str


@router.get('/discord')
async def get_discord_login_url() -> AuthUrlResponse:
	"""Get Discord OAuth authorization URL

	Returns the URL where the user should be redirected to authenticate with Discord.
	After successful authentication, Discord will redirect the user to the callback
	endpoint with an authorization code.

	Returns:
	    Discord OAuth authorization URL
	"""
	auth_url = get_discord_oauth_url()
	logger.info('Provided Discord login URL')
	return AuthUrlResponse(auth_url=auth_url)


@router.get('/discord/callback')
async def discord_oauth_callback(code: str = Query(...), request: Request = None) -> HTMLResponse:
	"""Handle Discord OAuth callback

	This endpoint receives the authorization code from Discord after the user
	grants permission. It exchanges the code for an access token, fetches the
	user's Discord information, and returns a JWT token for API access.

	Args:
	    code: Authorization code from Discord
	    request: FastAPI request object for template rendering

	Returns:
	    HTML page displaying the JWT access token

	Raises:
	    HTTPException 400 if OAuth exchange fails
	"""
	logger.info('Processing Discord OAuth callback')

	# Exchange authorization code for access token
	access_token = await exchange_code_for_token(code)
	if not access_token:
		logger.error('Failed to exchange Discord code for access token')
		raise HTTPException(status_code=400, detail='Failed to authenticate with Discord')

	# Fetch user information
	user_data = await get_discord_user(access_token)
	if not user_data:
		logger.error('Failed to fetch Discord user data')
		raise HTTPException(
			status_code=400, detail='Failed to retrieve user information from Discord'
		)

	# Extract user ID
	user_id_str = user_data.get('id')
	if not user_id_str:
		logger.error('No user ID in Discord response')
		raise HTTPException(status_code=400, detail='Invalid user data from Discord')

	discord_user_id = int(user_id_str)

	# Generate JWT token
	jwt_token = create_access_token(discord_user_id)

	logger.info(f'Successfully authenticated Discord user {discord_user_id}')

	# Return HTML template with the token
	return templates.TemplateResponse(
		'auth_response.html',
		{'request': request, 'access_token': jwt_token},
		media_type='text/html',
	)
