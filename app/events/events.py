from dataclasses import dataclass
from datetime import datetime
from app.models.schemas import GameStatsResponse


class Event:
    """Base class for all events."""

    def __post_init__(self):
        if not hasattr(self, "timestamp") or self.timestamp is None:
            self.timestamp = datetime.now(datetime.now().astimezone().tzinfo)


@dataclass
class AnalyzeImagesRequested(Event):
    """Event emitted when user requests image analysis via Discord"""

    image_one: bytes
    image_two: bytes | None
    discord_user_id: int
    discord_message_id: int
    discord_channel_id: int
    timestamp: datetime = None


@dataclass
class GameStatsAnalyzed(Event):
    """Event emitted after Gemini successfully analyzed game stats"""

    game_stats: GameStatsResponse
    discord_user_id: int
    discord_message_id: int
    discord_channel_id: int
    timestamp: datetime = None


@dataclass
class MatchSaved(Event):
    """Event emitted after match data is saved to MongoDB"""

    match_id: str
    discord_user_id: int
    discord_message_id: int
    discord_channel_id: int
    game_stats: GameStatsResponse
    timestamp: datetime = None
