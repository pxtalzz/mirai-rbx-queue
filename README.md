# 🛒 Discord Robux Queue Bot

A specialized Discord bot designed to manage and organize Robux order queues for your Discord server. This bot provides staff with powerful queue management tools while giving customers a simple way to check their position in line.

## ✨ Features

- **Live Queue Display**: Automatically updating queue embed in a designated channel
- **Staff-Only Management**: Only authorized staff can modify the queue
- **Customer Notifications**: Automatic DM notifications when customers reach #1 or their order is completed
- **Queue Persistence**: Queue data survives bot restarts using SQLite database
- **Duplicate Protection**: Prevents users from being added to the queue twice
- **Action Logging**: All queue actions logged to a dedicated log channel
- **Position Tracking**: Customers can check their queue position at any time
- **Flexible Queue Management**: Add, remove, move, and complete orders with ease

## 📋 Commands

### Staff Commands (Require Staff Role)

- `/queue add @user [amount]` - Add a customer to the queue
- `/queue remove @user` - Remove a customer from the queue
- `/queue complete @user` - Mark an order as completed and remove from queue
- `/queue move @user <position>` - Move a customer to a specific position
- `/queue clear` - Clear the entire queue (with confirmation)

### Customer Commands (Available to Everyone)

- `/queue position` - Check your position in the queue
- `/queue view` - View the current queue
- `/queue next` - See who is currently first in line

## 🚀 Setup Guide

### Prerequisites

- Python 3.8 or higher
- A Discord server
- A Discord bot token

### Step 1: Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section on the left sidebar
4. Click "Add Bot"
5. Under the TOKEN section, click "Copy" to copy your bot token
6. Save this token securely - you'll need it for the `.env` file

### Step 2: Configure Bot Permissions

1. Go to the "OAuth2" section in the left sidebar
2. Select "bot" under "SCOPES"
3. Under "PERMISSIONS", select the following:
   - Send Messages
   - Embed Links
   - Read Message History
   - Manage Messages (optional, for editing queue display)
4. Copy the generated URL and open it in your browser to invite the bot to your server

### Step 3: Get Your Server IDs

**Server ID:**
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click your server name and select "Copy Server ID"

**Staff Role ID:**
1. Right-click the staff role and select "Copy Role ID"

**Queue Channel ID:**
1. Right-click the channel where the queue will be displayed
2. Select "Copy Channel ID"

**Log Channel ID:**
1. Right-click the channel where actions will be logged
2. Select "Copy Channel ID"

### Step 4: Clone and Setup the Repository

```bash
# Clone the repository
git clone https://github.com/pxtalzz/robux-queue-bot.git
cd robux-queue-bot

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your values:
```
DISCORD_TOKEN=your_bot_token_here
SERVER_ID=your_server_id_here
STAFF_ROLE_ID=your_staff_role_id_here
QUEUE_CHANNEL_ID=your_queue_channel_id_here
LOG_CHANNEL_ID=your_log_channel_id_here
DATABASE_PATH=queue_data.db
```

### Step 6: Run the Bot

```bash
python main.py
```

You should see output like:
```
Loaded cog: queue_commands
Bot logged in as YourBotName#0000
Synced X command(s)
```

The bot is now running! 🎉

## 📖 Usage Guide

### For Staff

**Adding a customer to the queue:**
```
/queue add @Customer 30000
```
This adds the customer with an order for 30,000 Robux.

**Removing a customer:**
```
/queue remove @Customer
```

**Completing an order:**
```
/queue complete @Customer
```
This removes the customer and sends them a completion notification.

**Moving a customer:**
```
/queue move @Customer 3
```
This moves the customer to position #3.

**Clearing the queue:**
```
/queue clear
```
Requires confirmation to prevent accidental clears.

### For Customers

**Checking your position:**
```
/queue position
```

**Viewing the entire queue:**
```
/queue view
```

**Seeing who's next:**
```
/queue next
```

## 🗄️ Database

The bot uses **SQLite** for persistent storage. The database is automatically created on first run and stored in `queue_data.db`.

### Database Schema

```sql
CREATE TABLE queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    amount INTEGER,
    position INTEGER NOT NULL,
    notified INTEGER DEFAULT 0,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

The `notified` field prevents duplicate "you're next" notifications.

## 📧 Notifications

The bot sends automatic DM notifications:

1. **When added to queue**: Confirms they've been added
2. **When reaching #1**: "Your order is currently next in line!"
3. **When order is completed**: "Your Robux order has been completed. Thank you!"

Note: The bot will only send the "#1 notification" once to prevent spam.

## 🔧 Deployment Options

### Option 1: Local Machine
- Simply run `python main.py` on your computer
- Bot goes offline when computer sleeps
- Good for testing and small-scale use

### Option 2: Free Hosting (Replit)

1. Go to [Replit](https://replit.com)
2. Create a new Python project
3. Upload all files from this repository
4. Create `.env` file with your configuration
5. Run the bot
6. Use Replit's "Always On" feature (paid) to keep it running 24/7

### Option 3: Free Hosting (Railway)

1. Go to [Railway](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Add environment variables in Railway dashboard
5. Deploy and it will run 24/7

### Option 4: Paid Hosting (Heroku, AWS, DigitalOcean)

For production use, consider:
- **Heroku**: Free tier available (limited)
- **AWS EC2**: T2 micro tier free for 12 months
- **DigitalOcean**: Affordable droplets starting at $5/month

## 🐛 Troubleshooting

### Bot won't start
- Check your `DISCORD_TOKEN` is correct
- Ensure Python 3.8+ is installed
- Run `pip install -r requirements.txt`

### Commands not appearing
- Wait a few seconds after starting the bot
- Restart Discord client
- Make sure bot has permissions in the server

### Can't send messages in channels
- Make sure the bot has "Send Messages" permission
- Check that channel IDs in `.env` are correct

### Database errors
- Delete `queue_data.db` and restart the bot
- Make sure you have write permissions in the bot directory

## 📝 Project Structure

```
robux-queue-bot/
├── main.py                 # Bot entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── cogs/                  # Command implementations
│   └── queue_commands.py  # Queue management commands
├── database/              # Database management
│   └── queue_db.py        # SQLite database operations
└── utils/                 # Utility functions
    ├── queue_manager.py   # Queue display logic
    └── logger.py          # Action logging
```

## 🔐 Security Notes

- **Never commit `.env` file** - It contains your bot token
- Store your bot token securely
- Don't share your bot token with anyone
- Use role-based permissions (staff role) for management features
- The `.gitignore` file protects your `.env` from being committed

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📄 License

This project is open source and available under the MIT License.

## 💬 Support

If you encounter issues:
1. Check the Troubleshooting section
2. Review the Discord.py documentation: https://discordpy.readthedocs.io/
3. Check your `.env` configuration
4. Review bot permissions in your Discord server

## 🎯 Upcoming Features (Optional Additions)

- Queue history/statistics
- Custom queue channels per role
- Queue pause/resume functionality
- Estimated wait time calculations
- Web dashboard for queue management
- Multiple queue support
- Automatic timeout removal

---

Made with ❤️ for Robux sellers
