import discord
from discord.ext import commands
import logging

from app.events import AnalyzeImagesRequested, GeminiQueryRequested

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("Logged in as %s", bot.user)
    logger.debug("Logged in as %s", bot.user)


@bot.command()
async def ping(ctx):
    logger.info(f"ping command triggered by {ctx.author}")
    await ctx.send("Pong!")


@bot.command()
async def stats(ctx):
    """Analyzes game stats from two images using Gemini AI."""
    logger.info(f"stats command triggered by {ctx.author}")

    if not ctx.message.attachments:
        error_msg = "Please attach at least one image of your game stats."
        logger.warning(error_msg)
        await ctx.send(error_msg)
        return

    # reject any images of size > 10MB
    if any(attachment.size > 10_000_000 for attachment in ctx.message.attachments):
        error_msg = "Please attach images smaller than 10MB."
        logger.warning(error_msg)
        await ctx.send(error_msg)
        return

    if len(ctx.message.attachments) > 2:
        error_msg = "Please attach no more than two images: one for end-of-game stats and one for weapon stats."
        logger.warning(error_msg)
        await ctx.send(error_msg)
        return

    try:
        # Download both images
        logger.info(f"Downloading {len(ctx.message.attachments)} attachments...")
        image_one = await ctx.message.attachments[0].read()

        image_two = None
        if len(ctx.message.attachments) == 2:
            image_two = await ctx.message.attachments[1].read()

        # Include primitive identifiers (channel + message) in the event
        # so downstream handlers can reply without holding Discord context.

        # Emit event for analysis (decoupled from Discord)
        logger.info("Emitting AnalyzeImagesRequested event...")
        event = AnalyzeImagesRequested(
            image_one=image_one,
            image_two=image_two,
            discord_user_id=ctx.author.id,
            discord_message_id=ctx.message.id,
            discord_channel_id=ctx.channel.id,
        )
        await ctx.send("📊 Processing your stats... This may take a moment.")

        await ctx.bot.dispatcher.emit(event)


    except Exception as e:
        logger.error(f"Error in stats command: {str(e)}", exc_info=True)
        await ctx.send(f"❌ Error processing request: {str(e)}")

async def query(ctx, query_text):
    """Queries Gemini AI with user input and returns the response."""
    logger.info(f"query command triggered by {ctx.author} with query: {query_text}")

    try:
        # Emit event for querying Gemini (decoupled from Discord)
        logger.info("Emitting GeminiQueryRequested event...")
        event = GeminiQueryRequested(
            query=query_text,
            discord_user_id=ctx.author.id,
            discord_message_id=ctx.message.id,
            discord_channel_id=ctx.channel.id,
        )
        await ctx.send("🤖 Processing your query... This may take a moment.")

        await ctx.bot.dispatcher.emit(event)


    except Exception as e:
        logger.error(f"Error in query command: {str(e)}", exc_info=True)
        await ctx.send(f"❌ Error processing request: {str(e)}")