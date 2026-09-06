import discord
from discord.ext import commands
from discord import app_commands
import logging
from database.queue_db import QueueDB
from utils.queue_manager import QueueManager
from utils.logger import log_action
from config import STAFF_ROLE_ID, SERVER_ID

logger = logging.getLogger(__name__)

# Color constant
EMBED_COLOR = 0xf3f3f3

class QueueCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = QueueDB()
        self.queue_manager = QueueManager(bot, self.db)

    async def cog_load(self):
        await self.db.init_db()

    # Check if user is staff
    def is_staff():
        async def predicate(interaction: discord.Interaction) -> bool:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if not staff_role:
                await interaction.response.send_message(
                    "x_x Staff role not configured. Please contact an administrator.",
                    ephemeral=True
                )
                return False
            
            if staff_role not in interaction.user.roles:
                await interaction.response.send_message(
                    "x_x You don't have permission to use this command. Only staff can manage the queue.",
                    ephemeral=True
                )
                return False
            return True
        return app_commands.check(predicate)

    # Subcommand group for queue management
    queue_group = app_commands.Group(name="queue", description="Queue management commands")

    @queue_group.command(name="add", description="Add a customer to the queue")
    @app_commands.describe(user="The customer to add", amount="Robux amount (optional)")
    @is_staff()
    async def add_user(self, interaction: discord.Interaction, user: discord.User, amount: int = None):
        await interaction.response.defer()
        
        # Check if user is already in queue
        position = await self.db.get_user_position(user.id)
        if position is not None:
            await interaction.followup.send(
                f"(´；ω；`) {user.mention} is already in the queue at position #{position + 1}.",
                ephemeral=True
            )
            return
        
        # Add user to queue
        await self.db.add_to_queue(user.id, amount)
        await self.queue_manager.update_queue_display()
        
        # Send notification to customer
        try:
            await user.send(
                f"^^ **You've been added to the order queue!**\n"
                f"Your order: {amount:,} Robux" if amount else f"^^ **You've been added to the order queue!**\n"
                f"Your order has been added to the queue. Please wait for your turn! (´▽`)"
            )
        except discord.Forbidden:
            logger.warning(f"Could not DM user {user.id}")
        
        # Log the action
        await log_action(self.bot, interaction.user, user, "Added to queue", amount)
        
        await interaction.followup.send(
            f"{user.mention} has been added to the queue !*!* <a:pink_check:1543651964477382772>",
            ephemeral=True
        )

    @queue_group.command(name="remove", description="Remove a customer from the queue")
    @app_commands.describe(user="The customer to remove")
    @is_staff()
    async def remove_user(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer()
        
        # Check if user is in queue
        position = await self.db.get_user_position(user.id)
        if position is None:
            await interaction.followup.send(
                f"(´；ω；`) {user.mention} is not in the queue.",
                ephemeral=True
            )
            return
        
        # Remove user from queue
        await self.db.remove_from_queue(user.id)
        await self.queue_manager.update_queue_display()
        
        # Log the action
        await log_action(self.bot, interaction.user, user, "Removed from queue")
        
        await interaction.followup.send(
            f"{user.mention} has been removed from the queue (´▽`)",
            ephemeral=True
        )

    @queue_group.command(name="complete", description="Mark a customer's order as completed")
    @app_commands.describe(user="The customer who's order is complete")
    @is_staff()
    async def complete_order(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer()
        
        # Check if user is in queue
        position = await self.db.get_user_position(user.id)
        if position is None:
            await interaction.followup.send(
                f"(´；ω；`) {user.mention} is not in the queue.",
                ephemeral=True
            )
            return
        
        # Remove user from queue
        await self.db.remove_from_queue(user.id)
        await self.queue_manager.update_queue_display()
        
        # Send completion notification to customer
        try:
            await user.send(
                f"^^ **Order Completed!**\n"
                f"Your Robux order has been completed. Thank you for ordering! (´▽`)"
            )
        except discord.Forbidden:
            logger.warning(f"Could not DM user {user.id}")
        
        # Log the action
        await log_action(self.bot, interaction.user, user, "Order completed")
        
        await interaction.followup.send(
            f"{user.mention}'s order has been completed and removed from the queue (´▽`)",
            ephemeral=True
        )

    @queue_group.command(name="move", description="Move a customer to a different position")
    @app_commands.describe(user="The customer to move", position="The new position (1-indexed)")
    @is_staff()
    async def move_user(self, interaction: discord.Interaction, user: discord.User, position: int):
        await interaction.response.defer()
        
        # Check if user is in queue
        current_position = await self.db.get_user_position(user.id)
        if current_position is None:
            await interaction.followup.send(
                f"(´；ω；`) {user.mention} is not in the queue.",
                ephemeral=True
            )
            return
        
        # Get queue length
        queue_length = await self.db.get_queue_length()
        
        # Validate new position
        if position < 1 or position > queue_length:
            await interaction.followup.send(
                f"(´；ω；`) Invalid position. Queue length is {queue_length}.",
                ephemeral=True
            )
            return
        
        # Move user
        await self.db.move_in_queue(user.id, position - 1)  # Convert to 0-indexed
        await self.queue_manager.update_queue_display()
        
        # Log the action
        await log_action(self.bot, interaction.user, user, f"Moved to position #{position}")
        
        await interaction.followup.send(
            f"{user.mention} has been moved to position #{position} (´▽`)",
            ephemeral=True
        )

    @queue_group.command(name="position", description="Check your position in the queue")
    async def check_position(self, interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer(ephemeral=True)
        
        # If no user specified, check the caller's position
        if user is None:
            user = interaction.user
        
        position = await self.db.get_user_position(user.id)
        
        if position is None:
            await interaction.followup.send(
                f"(´；ω；`) {user.mention} is not in the queue.",
                ephemeral=True
            )
            return
        
        queue_length = await self.db.get_queue_length()
        ahead = position
        
        embed = discord.Embed(
            title="your order !! <a:pinkexclaim:1543651783354753074>",
            description=f"you are currently #{position + 1} in the queue !*!*\n\n"
                       f"there are {ahead} orders ahead of you.\n\n"
                       f"please be patient while we process orders <a:dots:1543641369694961746>",
            color=EMBED_COLOR
        )
        embed.set_footer(text=f"Total in queue: {queue_length}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @queue_group.command(name="view", description="View the current queue")
    async def view_queue(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        queue_data = await self.db.get_queue()
        
        if not queue_data:
            embed = discord.Embed(
                title=":wind_chime:  ◠◠  rbx order qu__*eu*__e    ₊    !!",
                description="The queue is currently empty.",
                color=EMBED_COLOR
            )
        else:
            queue_text = "\n".join(
                [f"{i + 1}. <@{user_id}>" for i, (user_id, amount) in enumerate(queue_data)]
            )
            embed = discord.Embed(
                title=":wind_chime:  ◠◠  rbx order qu__*eu*__e    ₊    !!",
                description=queue_text,
                color=EMBED_COLOR
            )
            embed.set_footer(text=f"Total orders: {len(queue_data)}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @queue_group.command(name="next", description="Show who is currently first in line")
    async def show_next(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        queue_data = await self.db.get_queue()
        
        if not queue_data:
            await interaction.followup.send(
                "(´；ω；`) The queue is currently empty.",
                ephemeral=True
            )
            return
        
        next_user_id, amount = queue_data[0]
        embed = discord.Embed(
            title="^^ Next Order",
            description=f"<@{next_user_id}> is currently next in line!" +
                       (f"\nOrder: {amount:,} Robux" if amount else ""),
            color=EMBED_COLOR
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @queue_group.command(name="clear", description="Clear the entire queue (requires confirmation)")
    @is_staff()
    async def clear_queue(self, interaction: discord.Interaction):
        # Create a confirmation view
        class ConfirmView(discord.ui.View):
            def __init__(self, ctx_user):
                super().__init__()
                self.ctx_user = ctx_user
                self.confirmed = False
            
            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != self.ctx_user:
                    await interaction.response.send_message("You can't use this button.", ephemeral=True)
                    return
                
                self.confirmed = True
                await self.db.clear_queue()
                await self.queue_manager.update_queue_display()
                
                await log_action(self.bot, interaction.user, None, "Cleared entire queue")
                
                await interaction.response.send_message(
                    "The queue has been cleared (´▽`)",
                    ephemeral=True
                )
                self.stop()
            
            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != self.ctx_user:
                    await interaction.response.send_message("You can't use this button.", ephemeral=True)
                    return
                
                await interaction.response.send_message(
                    "Queue clear cancelled (´；ω；`)",
                    ephemeral=True
                )
                self.stop()
        
        view = ConfirmView(interaction.user)
        view.db = self.db
        view.queue_manager = self.queue_manager
        view.bot = self.bot
        
        await interaction.response.send_message(
            "(´；ω；`) Are you sure you want to clear the entire queue? This action cannot be undone.",
            view=view,
            ephemeral=True
        )

    # Set the queue_group as a command group
    def cogs_load(self):
        self.bot.tree.add_command(self.queue_group)

async def setup(bot):
    await bot.add_cog(QueueCommands(bot))
