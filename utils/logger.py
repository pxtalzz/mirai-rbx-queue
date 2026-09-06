import discord
import logging
from config import LOG_CHANNEL_ID, COLOR_INFO
from datetime import datetime

logger = logging.getLogger(__name__)

async def log_action(bot, staff_user: discord.User, customer_user: discord.User or None, action: str, amount: int = None):
    """Log queue actions to the log channel."""
    try:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if not channel:
            logger.warning(f"Log channel {LOG_CHANNEL_ID} not found")
            return
        
        description = f"**Staff:** {staff_user.mention}\n"
        
        if customer_user:
            description += f"**Customer:** {customer_user.mention}\n"
        
        description += f"**Action:** {action}\n"
        
        if amount:
            description += f"**Order Amount:** {amount:,} Robux\n"
        
        description += f"**Time:** <t:{int(datetime.now().timestamp())}:F>"
        
        embed = discord.Embed(
            title="📋 Queue Update",
            description=description,
            color=COLOR_INFO,
            timestamp=datetime.now()
        )
        
        await channel.send(embed=embed)
        logger.info(f"Logged action: {action}")
    except Exception as e:
        logger.error(f"Error logging action: {e}")
