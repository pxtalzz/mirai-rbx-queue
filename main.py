import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Load cogs
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f"Loaded cog: {filename}")
            except Exception as e:
                logger.error(f"Failed to load cog {filename}: {e}")

@bot.event
async def on_ready():
    logger.info(f"Bot logged in as {bot.user}")
    await load_cogs()
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in .env file")
        exit(1)
    bot.run(token)
