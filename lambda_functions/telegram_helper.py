"""
Simple Telegram notification helper for Lambda functions
Uses only requests library for HTTP calls
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class SimpleTelegramNotifier:
    """Simple Telegram notification class for Lambda functions."""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.user_id = os.getenv('TELEGRAM_USER_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_notification(self, message: str) -> bool:
        """Send a simple text notification."""
        if not self.bot_token or not self.user_id:
            logger.warning("Telegram credentials not configured")
            return False
            
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.user_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=data, timeout=10)
            success = response.status_code == 200
            
            if not success:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def send_trade_notification(self, trade_data: dict) -> bool:
        """Send trade notification."""
        try:
            message = f"""🔔 **Trade Executed**

📊 **Details:**
• Symbol: {trade_data.get('symbol', 'N/A')}
• Action: {trade_data.get('action', 'N/A')}
• Quantity: {trade_data.get('quantity', 'N/A')}
• Price: ₹{trade_data.get('price', 'N/A')}
• Strategy: {trade_data.get('strategy', 'N/A')}

💰 **P&L Impact:** ₹{trade_data.get('pnl_impact', '0')}
📈 **Portfolio Value:** ₹{trade_data.get('portfolio_value', 'N/A')}"""
            
            return self.send_notification(message)
            
        except Exception as e:
            logger.error(f"Failed to format trade notification: {e}")
            return False
    
    def send_daily_summary(self, summary_data: dict) -> bool:
        """Send daily trading summary."""
        try:
            message = f"""📈 **Daily Trading Summary**

💰 **Performance:**
• Today's P&L: ₹{summary_data.get('daily_pnl', '0')}
• Total Trades: {summary_data.get('total_trades', '0')}
• Win Rate: {summary_data.get('win_rate', '0')}%

📊 **Portfolio:**
• Current Value: ₹{summary_data.get('portfolio_value', 'N/A')}
• Available Margin: ₹{summary_data.get('available_margin', 'N/A')}
• Open Positions: {summary_data.get('open_positions', '0')}

🎯 **Strategy Performance:**
{summary_data.get('strategy_performance', 'No data available')}"""
            
            return self.send_notification(message)
            
        except Exception as e:
            logger.error(f"Failed to format daily summary: {e}")
            return False

# Create global instance
telegram_notifier = SimpleTelegramNotifier()

def send_notification(message: str) -> bool:
    """Global function to send notification."""
    return telegram_notifier.send_notification(message)

def send_trade_notification(trade_data: dict) -> bool:
    """Global function to send trade notification."""
    return telegram_notifier.send_trade_notification(trade_data)

def send_daily_summary(summary_data: dict) -> bool:
    """Global function to send daily summary."""
    return telegram_notifier.send_daily_summary(summary_data)