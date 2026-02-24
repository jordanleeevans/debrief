---
slug: /
sidebar_position: 1
---

# Introduction

**Debrief** is a Discord bot powered by Google's Gemini AI that extracts and analyzes Call of Duty: Black Ops 7 game statistics from screenshot images.

## What Can Debrief Do?

- **Screenshot Analysis** — Upload game screenshots and get structured stats extracted by AI
- **Natural Language Queries** — Ask questions about your match history in plain English
- **Match Storage** — All analyzed matches are saved to MongoDB for future reference
- **REST API** — Access your match data programmatically with OAuth/JWT authentication

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| [Discord.py](https://discordpy.readthedocs.io/) | Discord bot framework |
| [FastAPI](https://fastapi.tiangolo.com/) | REST API framework |
| [Google Gemini](https://ai.google.dev/) | AI-powered image analysis & NL queries |
| [MongoDB](https://www.mongodb.com/) | Match data persistence |
| [Pydantic](https://docs.pydantic.dev/) | Data validation & settings |
| [Docker](https://www.docker.com/) | Containerization & orchestration |
| [pytest](https://pytest.org/) | Testing framework |

## Next Steps

- [Getting Started](./getting-started.md) — Set up and run Debrief locally
- [Discord Commands](./features/discord-commands.md) — Learn the available bot commands
- [REST API](./features/rest-api.md) — Explore the API endpoints
- [Architecture](./architecture/overview.md) — Understand how the system is designed
