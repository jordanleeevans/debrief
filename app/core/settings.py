from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "scoreboard_db"
    MONGODB_USER: str = "admin"
    MONGODB_PASSWORD: str = "password"
    DISCORD_BOT_TOKEN: str = "secret_token"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
