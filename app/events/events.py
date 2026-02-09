from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.schemas import GameStatsResponse


class Event(BaseModel):
    """Base class for all events.

    Events represent facts - things that have already happened.
    They use past tense naming (GameStatsAnalyzed, MatchSaved).
    Events can have multiple subscribers.
    """

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the event occurred",
    )

    model_config = ConfigDict(
        # Events should be immutable once created
        frozen=True,
        # Allow arbitrary types for flexibility
        arbitrary_types_allowed=True,
    )


class GameStatsAnalyzed(Event):
    """Event emitted after Gemini successfully analyzed game stats"""

    game_stats: GameStatsResponse
    discord_user_id: int = Field(..., gt=0)
    discord_message_id: int = Field(..., gt=0)
    discord_channel_id: int = Field(..., gt=0)


class MatchSaved(Event):
    """Event emitted after match data is saved to MongoDB"""

    match_id: str = Field(..., min_length=1)
    discord_user_id: int = Field(..., gt=0)
    discord_message_id: int = Field(..., gt=0)
    discord_channel_id: int = Field(..., gt=0)
    game_stats: GameStatsResponse


class QueryExecuted(Event):
    """Event emitted after database query is successfully executed"""

    query: str = Field(..., min_length=1)
    db_response: list[dict[str, Any]]
    discord_user_id: int = Field(..., gt=0)
    discord_message_id: int = Field(..., gt=0)
    discord_channel_id: int = Field(..., gt=0)
