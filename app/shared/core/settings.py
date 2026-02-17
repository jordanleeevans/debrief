from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	# MongoDB
	MONGODB_URI: str = 'mongodb://localhost:27017'
	MONGODB_DB: str = 'scoreboard_db'
	MONGODB_USER: str = 'admin'
	MONGODB_PASSWORD: str = 'password'

	# Discord Bot
	DISCORD_BOT_TOKEN: str = 'secret_token'

	# Discord OAuth 2.0
	DISCORD_CLIENT_ID: str = 'your_client_id'
	DISCORD_CLIENT_SECRET: str = 'your_client_secret'
	DISCORD_REDIRECT_URI: str = 'http://localhost:8000/api/auth/discord/callback'

	# Gemini API
	GEMINI_API_KEY: str = 'secret_api_key'

	# JWT Configuration
	JWT_SECRET: str = 'your_jwt_secret_key_change_in_production'
	JWT_ALGORITHM: str = 'HS256'
	JWT_EXPIRATION: int = 3600  # 1 hour in seconds

	model_config = ConfigDict(env_file='.env')


settings = Settings()
