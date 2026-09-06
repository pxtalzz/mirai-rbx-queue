import os
from dotenv import load_dotenv

load_dotenv()

# Discord configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID', 0))
STAFF_ROLE_ID = int(os.getenv('STAFF_ROLE_ID', 0))
QUEUE_CHANNEL_ID = int(os.getenv('QUEUE_CHANNEL_ID', 0))
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', 0))
DATABASE_PATH = os.getenv('DATABASE_PATH', 'queue_data.db')

# Validate configuration
def validate_config():
    required_vars = ['DISCORD_TOKEN', 'SERVER_ID', 'STAFF_ROLE_ID', 'QUEUE_CHANNEL_ID', 'LOG_CHANNEL_ID']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")

# Colors for embeds
COLOR_SUCCESS = 0x2ecc71  # Green
COLOR_ERROR = 0xe74c3c   # Red
COLOR_INFO = 0x3498db    # Blue
COLOR_WARNING = 0xf39c12  # Orange
COLOR_QUEUE = 0x9b59b6   # Purple
