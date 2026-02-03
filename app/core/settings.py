from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "scoreboard_db"
    MONGODB_USER: str = "admin"
    MONGODB_PASSWORD: str = "password"

    class Config:
        env_file = ".env"


settings = Settings()
