"""
Telegram Trading Interface Stub - Simplified version without telegram library
Used for Lambda deployment where we use direct API calls instead
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class AdvancedTradingTelegram:
    """Stub class for compatibility - actual functionality in Lambda uses direct API calls"""
    
    def __init__(self, bot_token: str, user_id: int):
        self.bot_token = bot_token
        self.user_id = user_id
        logger.info("AdvancedTradingTelegram stub initialized")
    
    async def initialize(self):
        """Stub initialization"""
        logger.info("Telegram interface initialized (stub)")
        pass
    
    async def send_notification(self, message: str) -> bool:
        """Stub notification - actual implementation uses direct API calls"""
        logger.info(f"Advanced notification (stub): {message[:100]}...")
        return True
    
    async def send_trade_notification(self, trade_data: dict) -> bool:
        """Stub trade notification"""
        logger.info(f"Advanced trade notification (stub): {trade_data}")
        return True
    
    async def send_daily_summary(self, summary_data: dict) -> bool:
        """Stub daily summary"""
        logger.info(f"Daily summary (stub): {summary_data}")
        return True
    
    async def run(self):
        """Stub run method"""
        logger.info("Advanced Telegram bot running (stub)")
        while True:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Stub stop method"""
        logger.info("Advanced Telegram bot stopped (stub)")
        pass

def create_advanced_telegram_bot(bot_token: str, user_id: int) -> AdvancedTradingTelegram:
    """Create a stub advanced telegram bot for compatibility"""
    return AdvancedTradingTelegram(bot_token, user_id)