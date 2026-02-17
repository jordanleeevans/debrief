from app.bot.handlers.gemini import register_gemini_command_handlers
from app.bot.handlers.db import register_mongodb_event_handlers
from app.bot.handlers.discord import register_discord_event_handlers

__all__ = [
    "register_gemini_command_handlers",
    "register_mongodb_event_handlers",
    "register_discord_event_handlers",
]
