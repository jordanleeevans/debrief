import discord
from discord.ext import commands
import logging

from app.core.settings import settings
from app.services.gemini import GeminiClient

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

        # Initialize Gemini client (using FakeGeminiClient for testing due to API quota limits)
        logger.info("Initializing Gemini client...")
        gemini_client = GeminiClient(api_key=settings.GEMINI_API_KEY)

        # Send images to Gemini and get response
        logger.info("Sending images to Gemini for analysis...")
        game_stats = await gemini_client.generate_game_stats(image_one, image_two)

        # Log the response
        logger.info(f"Game stats received: {game_stats.model_dump()}")

        # Send response back to Discord
        await ctx.send(
            f"✅ Analysis complete!\n```json\n{game_stats.model_dump_json(indent=2)}\n```"
        )

    except Exception as e:
        logger.error(f"Error analyzing stats: {str(e)}", exc_info=True)
        await ctx.send(f"❌ Error analyzing stats: {str(e)}")
