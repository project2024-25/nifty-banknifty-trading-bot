"""
Telegram Bot Launcher Script

Simple script to launch and test the Telegram bot for the trading system.
This can be used for development and testing purposes.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

from src.integrations.telegram_bot import create_telegram_bot
from src.utils.logger import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


async def main():
    """Main function to launch the Telegram bot."""
    
    # Get credentials from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    user_id_str = os.getenv("TELEGRAM_USER_ID")
    
    # Validate credentials
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        print("Please add your Telegram bot token to the .env file:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return
    
    if not user_id_str:
        logger.error("TELEGRAM_USER_ID not found in environment variables")
        print("❌ Error: TELEGRAM_USER_ID not set")
        print("Please add your Telegram user ID to the .env file:")
        print("TELEGRAM_USER_ID=your_telegram_user_id")
        print("\nTo find your user ID:")
        print("1. Start a chat with @userinfobot on Telegram")
        print("2. Send /start command")
        print("3. Copy the ID number it gives you")
        return
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        logger.error(f"Invalid TELEGRAM_USER_ID: {user_id_str}")
        print("❌ Error: TELEGRAM_USER_ID must be a valid number")
        return
    
    # Create and initialize bot
    try:
        print("🤖 Initializing Telegram bot...")
        bot = create_telegram_bot(bot_token, user_id)
        
        print("🔄 Starting bot initialization...")
        await bot.initialize()
        
        print("✅ Bot initialized successfully!")
        print(f"📱 Authorized user ID: {user_id}")
        print("🚀 Bot is now running...")
        print("\nTo test the bot:")
        print("1. Open Telegram")
        print("2. Start a chat with your bot")
        print("3. Send /start command")
        print("\nPress Ctrl+C to stop the bot")
        
        # Run the bot
        await bot.run()
        
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
        print(f"❌ Error starting bot: {e}")
        print("\nCommon issues:")
        print("1. Invalid bot token")
        print("2. Network connectivity issues")
        print("3. Missing dependencies")
        print("\nCheck the logs for more details.")


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'python-telegram-bot',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


if __name__ == "__main__":
    print("🤖 Telegram Trading Bot Launcher")
    print("=" * 40)
    
    # Check dependencies first
    if not check_dependencies():
        exit(1)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
        print("Goodbye! 👋")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        logging.error(f"Unexpected error in main: {e}")