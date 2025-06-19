Here are the config and environment files:

## config.py
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Bot Configuration Class"""
    
    # Required Settings
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Optional Settings
    BOT_NAME = os.getenv('BOT_NAME', 'ᴘʀᴏ ʀᴏʙᴏᴛ')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # Bot Settings
    DROP_PENDING_UPDATES = os.getenv('DROP_PENDING_UPDATES', 'True').lower() == 'true'
    WEBHOOK_MODE = os.getenv('WEBHOOK_MODE', 'False').lower() == 'true'
    
    # Webhook Settings (if using webhook instead of polling)
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8443'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required! Please set it in .env file")
        
        if cls.WEBHOOK_MODE and not cls.WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL is required when WEBHOOK_MODE is enabled")
        
        return True

# Create config instance
config = Config()

# Validate configuration on import
config.validate()
