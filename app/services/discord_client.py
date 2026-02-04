import discord
from discord.ext import commands

import logging

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
    await ctx.send("Pong!")
