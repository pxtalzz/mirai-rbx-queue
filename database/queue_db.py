import aiosqlite
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class QueueDB:
    def __init__(self):
        self.db_path = DATABASE_PATH

    async def init_db(self):
        """Initialize the database and create tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    amount INTEGER,
                    position INTEGER NOT NULL,
                    notified INTEGER DEFAULT 0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()
            logger.info("Database initialized successfully")

    async def add_to_queue(self, user_id: int, amount: int = None) -> int:
        """Add a user to the end of the queue."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM queue")
            result = await cursor.fetchone()
            position = result[0] if result else 0
            
            await db.execute(
                "INSERT INTO queue (user_id, amount, position) VALUES (?, ?, ?)",
                (user_id, amount, position)
            )
            await db.commit()
            logger.info(f"User {user_id} added to queue at position {position}")
            return position

    async def remove_from_queue(self, user_id: int) -> bool:
        """Remove a user from the queue and update positions."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT position FROM queue WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            
            if result is None:
                return False
            
            removed_position = result[0]
            
            # Delete the user
            await db.execute("DELETE FROM queue WHERE user_id = ?", (user_id,))
            
            # Update positions for users after this position
            await db.execute(
                "UPDATE queue SET position = position - 1 WHERE position > ?",
                (removed_position,)
            )
            
            await db.commit()
            logger.info(f"User {user_id} removed from queue")
            return True

    async def get_user_position(self, user_id: int) -> int or None:
        """Get a user's position in the queue (0-indexed)."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT position FROM queue WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            return result[0] if result else None

    async def get_queue(self) -> list:
        """Get the entire queue as a list of (user_id, amount) tuples."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id, amount FROM queue ORDER BY position ASC"
            )
            results = await cursor.fetchall()
            return results

    async def get_queue_length(self) -> int:
        """Get the number of users in the queue."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM queue")
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def move_in_queue(self, user_id: int, new_position: int) -> bool:
        """Move a user to a new position in the queue."""
        async with aiosqlite.connect(self.db_path) as db:
            # Get current position
            cursor = await db.execute(
                "SELECT position FROM queue WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            
            if result is None:
                return False
            
            current_position = result[0]
            
            if current_position == new_position:
                return True
            
            if current_position < new_position:
                # Moving down (backwards in queue)
                await db.execute(
                    "UPDATE queue SET position = position - 1 WHERE position > ? AND position <= ?",
                    (current_position, new_position)
                )
            else:
                # Moving up (forwards in queue)
                await db.execute(
                    "UPDATE queue SET position = position + 1 WHERE position >= ? AND position < ?",
                    (new_position, current_position)
                )
            
            # Update the user's position
            await db.execute(
                "UPDATE queue SET position = ? WHERE user_id = ?",
                (new_position, user_id)
            )
            
            await db.commit()
            logger.info(f"User {user_id} moved from position {current_position} to {new_position}")
            return True

    async def clear_queue(self) -> bool:
        """Clear the entire queue."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM queue")
            await db.commit()
            logger.info("Queue cleared")
            return True

    async def mark_notified(self, user_id: int) -> bool:
        """Mark a user as notified (for preventing duplicate notifications)."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE queue SET notified = 1 WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
            return True

    async def get_notified_status(self, user_id: int) -> bool:
        """Check if a user has been notified."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT notified FROM queue WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            return result[0] == 1 if result else False
