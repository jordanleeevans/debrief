from pydantic import BaseModel, Field, ConfigDict


class Command(BaseModel):
    """Base class for all commands.

    Commands represent an intent to perform an action.
    They use imperative naming (AnalyzeImages, QueryDatabase).
    Each command should have exactly one handler.
    """

    model_config = ConfigDict(
        # Allow arbitrary types like bytes
        arbitrary_types_allowed=True,
        # Make instances immutable (commands shouldn't change after creation)
        frozen=True,
    )


class AnalyzeImagesCommand(Command):
    """Command to analyze game stats from images using Gemini AI"""

    image_one: bytes
    image_two: bytes | None = None
    discord_user_id: int = Field(..., gt=0, description="Discord user ID")
    discord_message_id: int = Field(..., gt=0, description="Discord message ID")
    discord_channel_id: int = Field(..., gt=0, description="Discord channel ID")


class QueryDatabaseCommand(Command):
    """Command to query the database using natural language via Gemini"""

    query: str = Field(..., min_length=1, description="Natural language query")
    discord_user_id: int = Field(..., gt=0, description="Discord user ID")
    discord_message_id: int = Field(..., gt=0, description="Discord message ID")
    discord_channel_id: int = Field(..., gt=0, description="Discord channel ID")
