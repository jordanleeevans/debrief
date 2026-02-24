---
sidebar_position: 6
---

# Configuration

All configuration is managed through environment variables, loaded via Pydantic Settings.

## Environment Variables

Create a `.env` file in the project root:

```env
# Discord
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key

# MongoDB
MONGODB_URI=mongodb://mongo:27017
MONGODB_DB=scoreboard_db

# JWT
JWT_SECRET_KEY=your_secret_key_here
```

## Variable Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | Yes | Token from the [Discord Developer Portal](https://discord.com/developers/applications) |
| `DISCORD_CLIENT_ID` | Yes | OAuth2 client ID for your Discord application |
| `DISCORD_CLIENT_SECRET` | Yes | OAuth2 client secret |
| `DISCORD_REDIRECT_URI` | Yes | OAuth2 callback URL (must match portal config) |
| `GEMINI_API_KEY` | Yes | API key from [Google AI Studio](https://aistudio.google.com/) |
| `MONGODB_URI` | Yes | MongoDB connection string |
| `MONGODB_DB` | Yes | Database name |
| `JWT_SECRET_KEY` | Yes | Secret key for signing JWT tokens |

## Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Navigate to **Bot** → **Add Bot**
4. Copy the bot token → `DISCORD_BOT_TOKEN`
5. Under **OAuth2**, copy the client ID → `DISCORD_CLIENT_ID` and client secret → `DISCORD_CLIENT_SECRET`
6. Add your redirect URI under **OAuth2 → Redirects**
7. Invite the bot to your server using the OAuth2 URL Generator with `bot` scope and appropriate permissions

## Pydantic Settings

Configuration is loaded in `app/shared/core/settings.py` using `pydantic-settings`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    discord_bot_token: str
    gemini_api_key: str
    mongodb_uri: str
    mongodb_db: str
    # ... etc
```

Environment variables are automatically mapped to settings fields (case-insensitive).
