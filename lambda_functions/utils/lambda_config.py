"""
Lambda Configuration Management
Lightweight config for AWS Lambda environment
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration class for Lambda trading functions."""
    
    # Kite Connect API
    kite_api_key: str
    kite_api_secret: str
    kite_access_token: Optional[str] = None
    
    # Trading configuration
    enable_paper_trading: bool = True
    trading_capital: float = 100000
    max_daily_loss_percent: float = 3
    max_position_size_percent: float = 10
    
    # Database
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_user_id: int = 0
    
    # Risk management
    max_trades_per_day: int = 10
    max_loss_per_trade: float = 5000
    max_positions: int = 5

def get_lambda_config() -> Config:
    """Get configuration from environment variables for Lambda."""
    try:
        config = Config(
            # Kite API
            kite_api_key=os.getenv('KITE_API_KEY', ''),
            kite_api_secret=os.getenv('KITE_API_SECRET', ''),
            kite_access_token=os.getenv('KITE_ACCESS_TOKEN'),
            
            # Trading
            enable_paper_trading=os.getenv('ENABLE_PAPER_TRADING', 'true').lower() == 'true',
            trading_capital=float(os.getenv('TRADING_CAPITAL', '100000')),
            max_daily_loss_percent=float(os.getenv('MAX_DAILY_LOSS_PERCENT', '3')),
            max_position_size_percent=float(os.getenv('MAX_POSITION_SIZE_PERCENT', '10')),
            
            # Database
            supabase_url=os.getenv('SUPABASE_URL'),
            supabase_key=os.getenv('SUPABASE_KEY'),
            
            # Telegram
            telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
            telegram_user_id=int(os.getenv('TELEGRAM_USER_ID', '0')),
            
            # Risk
            max_trades_per_day=int(os.getenv('MAX_TRADES_PER_DAY', '10')),
            max_loss_per_trade=float(os.getenv('MAX_LOSS_PER_TRADE', '5000')),
            max_positions=int(os.getenv('MAX_POSITIONS', '5'))
        )
        
        logger.info("Configuration loaded successfully")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def validate_config(config: Config) -> bool:
    """Validate that required configuration is present."""
    try:
        # Required fields
        if not config.kite_api_key:
            logger.error("KITE_API_KEY is required")
            return False
        
        if not config.kite_api_secret:
            logger.error("KITE_API_SECRET is required")
            return False
        
        if not config.enable_paper_trading and not config.kite_access_token:
            logger.error("KITE_ACCESS_TOKEN is required for live trading")
            return False
        
        if config.trading_capital <= 0:
            logger.error("TRADING_CAPITAL must be positive")
            return False
        
        if config.telegram_user_id == 0:
            logger.warning("TELEGRAM_USER_ID not set - notifications disabled")
        
        logger.info("Configuration validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False