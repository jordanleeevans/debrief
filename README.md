# Debrief

![CI](https://github.com/jordanleeevans/debrief/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/jordanleeevans/debrief/branch/main/graph/badge.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Discord bot powered by Google's Gemini AI that automatically extracts and analyzes Call of Duty: Black Ops 7 game statistics from screenshot images.

![An example of a discord bot taking a request via the `!stats` command and returning a result from Gemini AI](./public/analysis-example.gif)

## Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Discord Commands](#discord-commands)
- [REST API](#rest-api)
- [Architecture](#architecture)
- [Development](#development)
- [Supported Data](#supported-data)

---

## Features

- **AI-Powered OCR** - Gemini 2.5 Flash Lite extracts stats from game screenshots
- **Discord Bot** - `!stats` and `!query` commands for analysis and database queries
- ️**CQRS Architecture** - Clean separation of Commands and Events
- **MongoDB Storage** - Persistent stats tracking with aggregation pipelines
- **OAuth Authentication** - Discord OAuth 2.0 with JWT tokens
- **Type-Safe** - Pydantic models for all data validation
- **Hot Reload** - Docker Compose watch mode for fast development

## Quick Start

**Prerequisites:** Docker, [Discord Bot Token](https://discord.com/developers/docs/intro), [Google Gemini API Key](https://aistudio.google.com/)

```bash
# Clone and configure
git clone <repository-url>
cd debrief
cp .env.example .env

# Edit .env with your tokens
# Start services
docker compose up --build -d

# Or use watch mode for development
docker compose watch
```

## Configuration

Create `.env` in the project root:

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

## Discord Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `!ping` | Health check | `!ping` |
| `!stats` | Extract stats from screenshots (1-2 images, <10MB each) | `!stats` + attach images |
| `!query` | Natural language database queries | `!query how many kills on Raid?` |

## REST API

**Base URL:** `http://localhost:8000`

### Authentication
- **`GET /auth/login`** - Initiate Discord OAuth flow
- **`GET /auth/callback`** - OAuth callback (redirected from Discord)

### Matches (Protected)
- **`GET /api/matches`** - List user's matches
  - Query params: `limit` (1-100, default: 10), `skip` (default: 0)
  - Requires: `Authorization: Bearer <jwt_token>`

## Architecture

### Process Separation

```mermaid
graph TB
    subgraph Discord["Discord Bot (bot.py)"]
        CMD[Commands]
        EVT[Events]
    end
    
    subgraph API["FastAPI App (main.py)"]
        REST[REST API]
        AUTH[OAuth/JWT]
    end
    
    DB[(MongoDB)]
    
    Discord <--> DB
    API <--> DB
    
    style Discord fill:#5865F2,stroke:#4752C4,color:#fff
    style API fill:#009688,stroke:#00796B,color:#fff
    style DB fill:#47A248,stroke:#3E8E41,color:#fff
```

- **bot.py** - Discord bot process with command handlers
- **main.py** - FastAPI REST API with OAuth and JWT authentication
- **MongoDB** - Shared database for both services

### CQRS Pattern

**Commands**
- `AnalyzeImagesCommand` → Analyze game screenshots
- `QueryDatabaseCommand` → Query match database

**Events**
- `GameStatsAnalyzed` → Stats extracted from images
- `MatchSaved` → Match persisted to database
- `QueryExecuted` → Database query completed

**Flow:**
1. Discord command → Command created
2. CommandBus executes handler (1:1)
3. Handler emits Event(s)
4. EventDispatcher notifies subscribers (1:many)
5. Subscribers react (save to DB, send Discord message, etc.)

## Development

### Setup

```bash
# Install dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

```

### Project Structure

```
app/
├── auth/          # OAuth, JWT, authentication
├── commands/      # Command definitions and CommandBus
├── events/        # Event definitions and EventDispatcher
├── handlers/      # Command handlers and event subscribers
├── services/      # Discord bot and Gemini client
├── models/        # Pydantic schemas and types
├── db/            # MongoDB connection
└── tests/         # Unit and integration tests
```

## Supported Data

### Game Modes
- Hardpoint
- Search and Destroy
- Overload

### Maps
- Scar
- Raid
- Exposure
- Den
- Colossus
- Blackheart

### Teams
- Team Guild
- JSOC

### Weapons
- M15 Mod 0
- Peacekeeper MK1
- Dravec 45
- VS Recon
- Jäger 45
- Coda 9
- Knife

---

**Tech Stack:** FastAPI · Discord.py · Pydantic · MongoDB · Google Gemini · Docker · pytest
