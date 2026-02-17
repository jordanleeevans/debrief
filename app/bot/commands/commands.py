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


class DiscordCommand(Command):
    """Base class for commands that originate from Discord interactions.

    These commands include metadata about the Discord user, message, and channel
    that triggered the command. This allows handlers to send responses back to
    the correct place in Discord.
    """

    discord_user_id: int = Field(..., gt=0, description="Discord user ID")
    discord_message_id: int = Field(..., gt=0, description="Discord message ID")
    discord_channel_id: int = Field(..., gt=0, description="Discord channel ID")


class AnalyzeImagesCommand(DiscordCommand):
    """Command to analyze game stats from images using Gemini AI."""

    image_one: bytes = Field(..., description="First image (end-of-game stats)")
    image_two: bytes | None = Field(None, description="Second image (weapon stats)")


class QueryDatabaseCommand(DiscordCommand):
    """Command to query database using natural language."""

    query: str = Field(..., min_length=1, description="Natural language query")
