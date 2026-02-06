# Debrief API

A Discord bot powered by Google's Gemini AI that automatically extracts and analyzes Call of Duty: Black Ops 7 game statistics from screenshot images.

## 📋 Overview

Debrief is a FastAPI-based Discord bot that leverages Google's Gemini 2.5 Flash model to intelligently extract player statistics from Call of Duty game screenshots. Users can upload two images (end-of-game stats and weapon stats) in Discord, and the bot will automatically parse the data and return structured JSON with all the relevant statistics.

### Use Case

- **Competitive Gaming Teams**: Track player performance metrics automatically without manual data entry
- **Personal Stats Tracking**: Build a historical database of game statistics for analysis and improvement tracking

## ✨ Features

- **AI-Powered Image Recognition**: Uses Gemini 2.5 Flash to accurately extract statistics from game screenshots
- **Discord Integration**: Simple Discord commands for easy access
- **Structured Data Extraction**: Returns validated JSON with weapon stats, scoreboard data, and game information
- **ALL Rank Game Modes Support**: Handles Hardpoint, Search and Destroy, and Overload modes with mode-specific scoreboards

## 🛠️ Prerequisites

- **Docker & Docker Compose** - For containerization
- **Python 3.12+** - If running locally
- **Discord Bot Token** - Create one at [Discord Developer Portal](https://discord.com/developers/applications)
- **Google Gemini API Key** - Get one from [Google AI Studio](https://ai.google.dev/)
- **MongoDB** - For stats storage (included in Docker Compose)

## 🚀 Setup & Installation

### Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd debrief
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure .env**
   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   MONGODB_URI=mongodb://admin:password@mongo:27017
   MONGODB_DB=scoreboard_db
   MONGODB_USER=admin
   MONGODB_PASSWORD=password
   ```

4. **Start the application**
   ```bash
   docker compose up --build -d
   ```

## 🎮 Discord Commands

### `/ping`
Health check command to verify the bot is running.
```
!ping
→ Pong!
```

### `/stats`
Analyzes game statistics from uploaded images.

**Usage:**
```
!stats
[Attach 1-2 images]
```

**Requirements:**
- At least 1 image (either stats or weapon stats)
- Maximum 2 images
- Each image must be under 10MB
- PNG format recommended

**Response:**
```json
{
  "primary_weapon_stats": {
    "primary_weapon_name": "M15 MOD 0",
    "eliminations": 50,
    "elimination_death_ratio": 2.5,
    ...
  },
  "secondary_weapon_stats": {...},
  "melee_weapon_stats": {...},
  "map": "SCAR",
  "game_mode": "HARDPOINT",
  "team": "TEAM GUILD",
  "scoreboard": {...}
}
```

## 🏗️ Project Structure

```
debrief/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   └── settings.py         # Configuration management
│   ├── db/
│   │   └── mongo.py            # MongoDB connection
│   ├── models/
│   │   ├── enums.py            # Game enums (maps, modes, teams, weapons)
│   │   ├── types.py            # Type definitions
│   │   └── schemas.py          # Pydantic models for data validation
│   └── services/
│       ├── discord_client.py   # Discord bot and commands
│       └── gemini.py           # Gemini API client
├── tests/                      # Test suite
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── pyproject.toml              # Python project configuration
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Discord bot token (required) | `secret_token` |
| `GEMINI_API_KEY` | Google Gemini API key (required) | `secret_api_key` |
| `MONGODB_URI` | MongoDB connection URI | `mongodb://localhost:27017` |
| `MONGODB_DB` | MongoDB database name | `scoreboard_db` |
| `MONGODB_USER` | MongoDB username | `admin` |
| `MONGODB_PASSWORD` | MongoDB password | `password` |

## 📊 Supported Game Data

### Maps
- SCAR
- RAID
- EXPOSURE
- DEN
- COLOSSUS
- BLACKHEART

### Game Modes
- HARDPOINT
- SEARCH AND DESTROY
- OVERLOAD

### Teams
- TEAM GUILD
- JSOC

### Weapons

**Primary Weapons:**
- M15 MOD 0
- PEACEKEEPER MK1
- DRAVEC 45 (SMG)
- VS RECON (Sniper)

**Secondary Weapons:**
- JÄGER 45
- CODA 9

**Melee Weapons:**
- Any string value (Combat Knife, etc.)

## 🧪 Testing

```bash
pytest tests/
```

## 📦 Dependencies

- **FastAPI**: Web framework
- **discord.py**: Discord bot library
- **pydantic**: Data validation
- **pymongo**: MongoDB driver
- **google-genai**: Google Gemini API client
- **pydantic-settings**: Configuration management

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly (use FakeGeminiClient to avoid quota issues)
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📚 Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
