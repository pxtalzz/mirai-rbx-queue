import discord
import logging
from config import QUEUE_CHANNEL_ID, COLOR_QUEUE

logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.message_id = None

    async def update_queue_display(self):
        """Update the queue embed in the designated channel."""
        try:
            channel = self.bot.get_channel(QUEUE_CHANNEL_ID)
            if not channel:
                logger.error(f"Queue channel {QUEUE_CHANNEL_ID} not found")
                return
            
            queue_data = await self.db.get_queue()
            queue_length = len(queue_data)
            
            if queue_length == 0:
                embed = discord.Embed(
                    title="🛒 ROBux ORDER QUEUE",
                    description="The queue is currently empty.",
                    color=COLOR_QUEUE
                )
            else:
                queue_text = "\n".join(
                    [f"{i + 1}. <@{user_id}>" + (f" | {amount:,} Robux" if amount else "")
                     for i, (user_id, amount) in enumerate(queue_data)]
                )
                embed = discord.Embed(
                    title="🛒 ROBux ORDER QUEUE",
                    description=queue_text,
                    color=COLOR_QUEUE
                )
            
            embed.set_footer(text=f"Total orders: {queue_length}")
            
            # Find and update existing message or create a new one
            try:
                async for message in channel.history(limit=10):
                    if message.author == self.bot.user and message.embeds:
                        await message.edit(embed=embed)
                        logger.info("Queue display updated")
                        return
                
                # If no message found, send a new one
                msg = await channel.send(embed=embed)
                self.message_id = msg.id
                logger.info("New queue display message created")
            except discord.Forbidden:
                logger.error(f"No permission to send message in channel {QUEUE_CHANNEL_ID}")
        except Exception as e:
            logger.error(f"Error updating queue display: {e}")

    async def check_and_notify_next_in_line(self):
        """Check if someone is next in line and send them a DM notification."""
        try:
            queue_data = await self.db.get_queue()
            
            if not queue_data:
                return
            
            next_user_id, _ = queue_data[0]
            already_notified = await self.db.get_notified_status(next_user_id)
            
            if not already_notified:
                user = self.bot.get_user(next_user_id)
                if user:
                    try:
                        await user.send(
                            f"🔔 **Your order is currently next in line!**\n"
                            f"Please be ready with your information. Your order will be processed soon! ♡"
                        )
                        await self.db.mark_notified(next_user_id)
                        logger.info(f"Notified user {next_user_id} that they are next in line")
                    except discord.Forbidden:
                        logger.warning(f"Could not DM user {next_user_id}")
        except Exception as e:
            logger.error(f"Error in check_and_notify_next_in_line: {e}")
