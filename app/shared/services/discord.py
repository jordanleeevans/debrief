import discord
from discord.ext import commands
import logging

from app.bot.commands import AnalyzeImagesCommand, QueryDatabaseCommand

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.debug("Logged in as %s", bot.user)


@bot.command()
async def ping(ctx):
    logger.info(f"ping command triggered by {ctx.author}")
    await ctx.send("Pong!")


@bot.command()
async def stats(ctx):
    """Analyzes game stats from two images using Gemini AI."""
    logger.info(f"stats command triggered by {ctx.author}")

    try:
        _validate_attachments(ctx.message.attachments)

        logger.info("Downloading attachments...")
        image_one, image_two = await _download_images(ctx.message.attachments)

        await ctx.send("📊 Processing your stats... This may take a moment.")
        logger.info("Executing AnalyzeImagesCommand...")
        await _execute_analyze_command(ctx, image_one=image_one, image_two=image_two)

    except ValueError as e:
        # Validation errors are expected user-facing problems
        msg = str(e)
        logger.warning(msg)
        await ctx.send(msg)

    except Exception as e:
        logger.error(f"Error in stats command: {str(e)}", exc_info=True)
        await ctx.send(f"❌ Error processing request: {str(e)}")


def _validate_attachments(attachments):
    if not attachments:
        raise ValueError("Please attach at least one image of your game stats.")

    # reject any images of size > 10MB
    if any(attachment.size > 10_000_000 for attachment in attachments):
        raise ValueError("Please attach images smaller than 10MB.")

    if len(attachments) > 2:
        raise ValueError(
            "Please attach no more than two images: one for end-of-game stats and one for weapon stats."
        )


async def _download_images(attachments):
    # Assumes attachments are validated (1 or 2 attachments, sizes ok)
    image_one = await attachments[0].read()
    image_two = None
    if len(attachments) == 2:
        image_two = await attachments[1].read()
    return image_one, image_two


async def _execute_analyze_command(ctx, *, image_one, image_two=None):
    command = AnalyzeImagesCommand(
        image_one=image_one,
        image_two=image_two,
        discord_user_id=ctx.author.id,
        discord_message_id=ctx.message.id,
        discord_channel_id=ctx.channel.id,
    )

    await ctx.bot.command_bus.execute(command)


@bot.command()
async def query(ctx):
    """Queries Gemini AI with user input and returns the response."""

    message_content = ctx.message.content[len("!query ") :].strip()

    if not message_content:
        error_msg = "Please provide a query after the command. For example: `!query What are some tips for improving my aim?`"
        logger.warning(error_msg)
        await ctx.send(error_msg)
        return

    logger.info(
        f"query command triggered by {ctx.author} with query: {message_content}"
    )

    try:
        # Execute COMMAND (not event) - commands represent intent
        logger.info("Executing QueryDatabaseCommand...")
        await ctx.send("🤖 Processing your query... This may take a moment.")
        command = QueryDatabaseCommand(
            query=message_content,
            discord_user_id=ctx.author.id,
            discord_message_id=ctx.message.id,
            discord_channel_id=ctx.channel.id,
        )
        await ctx.bot.command_bus.execute(command)

    except Exception as e:
        logger.error(f"Error in query command: {str(e)}", exc_info=True)
        await ctx.send(f"❌ Error processing request: {str(e)}")
