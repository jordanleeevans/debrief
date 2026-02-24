---
sidebar_position: 2
---

# Getting Started

Get Debrief up and running in a few minutes.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- A [Discord Bot Token](https://discord.com/developers/docs/intro)
- A [Google Gemini API Key](https://aistudio.google.com/)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/jordanleeevans/debrief.git
cd debrief
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=mongodb://mongo:27017
MONGODB_DB=scoreboard_db
JWT_SECRET_KEY=your_secret_key_here
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 3. Start services

```bash
docker compose up --build -d
```

This starts four containers:

| Service | Port | Description |
|---------|------|-------------|
| `debrief_api` | `8000` | FastAPI REST API |
| `debrief_bot` | — | Discord bot process |
| `debrief_mongo` | `27017` | MongoDB database |
| `debrief_mongo_express` | `8081` | MongoDB admin UI |

### 4. Verify

- **API Docs**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)
- **Mongo Express**: Visit [http://localhost:8081](http://localhost:8081)
- **Bot**: Send `!ping` in your Discord server

## Development Mode

Use Docker Compose watch mode for live-reloading during development:

```bash
docker compose watch
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run coverage run -m pytest
uv run coverage report
```
