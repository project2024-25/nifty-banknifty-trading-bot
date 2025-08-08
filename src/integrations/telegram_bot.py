"""
Telegram Bot Stub - Simplified version without telegram library dependency
Used for Lambda deployment where we use direct API calls instead
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class TradingBotTelegram:
    """Stub class for compatibility - actual functionality in minimal_server.py"""
    
    def __init__(self, bot_token: str, user_id: int):
        self.bot_token = bot_token
        self.user_id = user_id
        logger.info("TradingBotTelegram stub initialized")
    
    async def send_notification(self, message: str) -> bool:
        """Stub method - actual implementation uses direct API calls"""
        logger.info(f"Telegram notification (stub): {message[:100]}...")
        return True
    
    async def send_trade_notification(self, trade_data: dict) -> bool:
        """Stub method - actual implementation uses direct API calls"""
        logger.info(f"Trade notification (stub): {trade_data}")
        return True
    
    async def start(self):
        """Stub method"""
        logger.info("Telegram bot start (stub)")
        pass
    
    async def stop(self):
        """Stub method"""
        logger.info("Telegram bot stop (stub)")
        pass

def create_telegram_bot(bot_token: str, user_id: int) -> TradingBotTelegram:
    """Create a stub telegram bot for compatibility"""
    return TradingBotTelegram(bot_token, user_id)

# Module-level functions for compatibility
async def send_notification(message: str, bot_token: str = None, user_id: str = None) -> bool:
    """Module-level send_notification function for compatibility"""
    logger.info(f"Module-level notification (stub): {message[:100]}...")
    return True

async def send_trade_notification(trade_data: dict, bot_token: str = None, user_id: str = None) -> bool:
    """Module-level send_trade_notification function for compatibility"""
    logger.info(f"Module-level trade notification (stub): {trade_data}")
    return True

async def send_daily_summary(summary_data: dict, bot_token: str = None, user_id: str = None) -> bool:
    """Module-level send_daily_summary function for compatibility"""
    logger.info(f"Module-level daily summary (stub): {summary_data}")
    return True