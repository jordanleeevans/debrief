# Debrief

![CI](https://github.com/jordanleeevans/debrief/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/jordanleeevans/debrief/branch/main/graph/badge.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Discord bot powered by Google's Gemini AI that automatically extracts and analyzes Call of Duty: Black Ops 7 game statistics from screenshot images.

![An example of a discord bot taking a request via the `!stats` command and returning a result from Gemini AI](./public/analysis-example.gif)

## Features

- **AI-Powered OCR**: Gemini 2.5 Flash extracts stats from game screenshots
- **Discord Commands**: `/stats` and `/query` for analysis and database queries
- **CQRS Architecture**: Separate Command/Event handling with `CommandBus` and `EventDispatcher`
- **MongoDB Storage**: Persistent stats tracking with aggregation support
- **Type-Safe**: Pydantic models for all data validation

## Quick Start

**Prerequisites:** Docker, [Discord Bot Token](https://discord.com/developers/docs/intro), [Google Gemini API Key](https://aistudio.google.com/)

1. Clone and configure:
   ```bash
   git clone <repository-url>
   cd debrief
   cp .env.example .env
   # Edit .env with your tokens
   ```

2. Start with Docker:
   ```bash
   docker compose up --build -d
   ```

## Configuration

Create `.env` with:
```env
DISCORD_BOT_TOKEN=your_token
GEMINI_API_KEY=your_key
MONGODB_URI=mongodb://admin:password@mongo:27017
MONGODB_DB=scoreboard_db
```

## Commands

- **`/ping`** - Health check
- **`/stats`** - Upload 1-2 images (<10MB) to extract game stats
- **`/query <prompt>`** - Natural language database queries (e.g., "Show my last 5 matches")

## API Endpoints

### Matches
- **`GET /api/matches`** - List all matches (paginated, limit: 1-100, default: 10)

All endpoints return JSON with match documents and metadata.

## Architecture

**Process Separation:**
- `bot.py` - Discord bot runs independently with command handlers
- `main.py` - FastAPI server with OAuth authentication, JWT tokens, and match API
- `docker-compose.yml` - Two services (api on port 8000, bot with no exposed ports)

**CQRS Pattern:**
- **Commands** (`/commands`) - Intent to act (AnalyzeImagesCommand, QueryDatabaseCommand)
- **CommandBus** - Single handler per command, enforces 1:1 relationship
- **Events** (`/events`) - Facts (GameStatsAnalyzed, MatchSaved, QueryExecuted)
- **EventDispatcher** - Multiple subscribers per event, 1:many broadcast

**API & Authentication:**
- JWT tokens for stateless authentication (1-hour expiration)
- Discord OAuth 2.0 for user authentication
- Bearer token validation on protected routes
- User data isolation (users can only access their own matches)

**Key Components:**
- `main.py` - FastAPI app, registers handlers and bot
- `routes.py` - Match API endpoints with pagination support
- `auth/routes.py` - OAuth and token endpoints
- `auth/jwt.py` - JWT token creation and verification
- `services/discord.py` - Discord bot with slash commands
- `services/gemini.py` - Gemini AI client for image analysis
- `handlers/` - Command and event handlers
- `repositories.py` - MongoDB data access layer
- `models/schemas.py` - Pydantic models with validation

## Development

```bash
# Install dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run coverage run -m pytest
uv run coverage report -m
```

## Supported Data

### Maps
| Maps |
| --- |
| SCAR |
| RAID |
| EXPOSURE |
| DEN |
| COLOSSUS |
| BLACKHEART |

### Modes
| Modes |
| --- |
| HARDPOINT |
| SEARCH AND DESTROY |
| OVERLOAD |

### Teams
| Teams |
| --- |
| TEAM GUILD |
| JSOC |

### Weapons
| Weapons |
| --- |
| M15 MOD 0 |
| PEACEKEEPER MK1 |
| DRAVEC 45 |
| VS RECON |
| JÄGER 45 |
| CODA 9 |

---

**Tech Stack:** FastAPI · Discord.py · Pydantic · MongoDB · Google Gemini · pytest
