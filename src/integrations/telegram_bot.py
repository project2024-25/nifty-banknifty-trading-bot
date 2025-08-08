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