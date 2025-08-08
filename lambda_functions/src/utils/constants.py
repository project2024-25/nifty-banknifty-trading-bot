"""
Trading Bot Constants
Contains all constant values used throughout the application
"""
from enum import Enum

# Trading Instruments Configuration
INSTRUMENTS = {
    'NIFTY': {
        'index': 'NIFTY 50',
        'trading_symbol': 'NIFTY',
        'lot_size': 50,
        'strike_interval': 50,
        'weekly_expiry': 'Thursday',
        'monthly_expiry': 'Last Thursday'
    },
    'BANKNIFTY': {
        'index': 'NIFTY BANK',
        'trading_symbol': 'BANKNIFTY',
        'lot_size': 25,
        'strike_interval': 100,
        'weekly_expiry': 'Wednesday',
        'monthly_expiry': 'Last Thursday'
    }
}

# Strategy Allocations
CONSERVATIVE_STRATEGIES = {
    'iron_condor': {
        'allocation': 25,
        'max_loss': 2,
        'target_profit': 1.5,
        'entry_conditions': {
            'vix_range': (12, 20),
            'trend': 'sideways',
            'time_to_expiry': (7, 30)
        }
    },
    'bull_put_spread': {
        'allocation': 20,
        'max_loss': 3,
        'target_profit': 2,
        'entry_conditions': {
            'trend': 'bullish',
            'support_nearby': True
        }
    },
    'bear_call_spread': {
        'allocation': 15,
        'max_loss': 3,
        'target_profit': 2,
        'entry_conditions': {
            'trend': 'bearish',
            'resistance_nearby': True
        }
    }
}

AGGRESSIVE_STRATEGIES = {
    'long_straddle': {
        'allocation': 15,
        'max_loss': 5,
        'target_profit': 10,
        'entry_conditions': {
            'event': 'high_impact',
            'vix': '<15 or >25'
        }
    },
    'directional_options': {
        'allocation': 15,
        'max_loss': 100,  # % of premium
        'target_profit': 200,
        'entry_conditions': {
            'strong_trend': True,
            'momentum_confirmation': True
        }
    },
    'intraday_scalping': {
        'allocation': 10,
        'max_loss': 1,
        'target_profit': 0.5,
        'frequency': 'high'
    }
}

# Market Hours (IST)
MARKET_HOURS = {
    'pre_open': '09:00',
    'open': '09:15',
    'close': '15:30',
    'post_close': '16:00'
}

# Risk Management Limits
RISK_LIMITS = {
    'max_daily_loss': 0.03,  # 3% of capital
    'max_position_size': 0.10,  # 10% per position
    'max_open_positions': 5,
    'max_aggressive_exposure': 0.40,  # 40% in aggressive
    'min_capital_buffer': 0.20  # Keep 20% cash
}

# Telegram Commands
TELEGRAM_COMMANDS = {
    # Status Commands
    '/start': 'Initialize bot and show welcome message',
    '/status': 'Show current P&L, positions, and system health',
    '/positions': 'List all open positions with details',
    '/performance': 'Show today/week/month performance metrics',
    
    # Control Commands
    '/pause': 'Pause all trading activities',
    '/resume': 'Resume trading activities',
    '/stop': 'Stop and close all positions (emergency)',
    '/risk': 'Adjust risk level (low/medium/high)',
    
    # Strategy Commands
    '/strategies': 'Show active strategies and allocations',
    '/enable': 'Enable specific strategy',
    '/disable': 'Disable specific strategy',
    
    # Analysis Commands
    '/analysis': 'Get current market analysis',
    '/signals': 'Show pending trade signals',
    '/youtube': 'Latest YouTube insights summary',
    
    # Reporting Commands
    '/report': 'Generate detailed performance report',
    '/logs': 'Show recent trade logs',
    '/errors': 'Show system errors/warnings'
}

# Error Codes
ERROR_CODES = {
    'E001': 'Market data unavailable',
    'E002': 'Order placement failed',
    'E003': 'Risk limit exceeded',
    'E004': 'Strategy error',
    'E005': 'Database connection failed',
    'E006': 'Invalid signal format',
    'E007': 'Insufficient funds',
    'E999': 'Unknown error'
}

class OrderStatus(Enum):
    PENDING = "PENDING"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"

class TradeStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PARTIAL = "PARTIAL"

class StrategyType(Enum):
    CONSERVATIVE = "CONSERVATIVE"
    AGGRESSIVE = "AGGRESSIVE"

# Feature Engineering Features
FEATURES = {
    'price_based': [
        'returns_1d', 'returns_5d', 'returns_20d',
        'volatility_realized', 'volatility_garch',
        'price_momentum', 'mean_reversion_score'
    ],
    'technical': [
        'rsi', 'macd_signal', 'bollinger_position',
        'atr_normalized', 'adx', 'volume_ratio'
    ],
    'options_specific': [
        'put_call_ratio', 'max_pain', 'open_interest_change',
        'implied_volatility_rank', 'iv_percentile',
        'gamma_exposure', 'options_flow'
    ],
    'sentiment': [
        'youtube_sentiment', 'reddit_sentiment',
        'fear_greed_index', 'vix_level'
    ]
}

# YouTube Channels Configuration
YOUTUBE_CHANNELS = {
    'sensibull': {
        'channel_id': 'UC...',  # To be configured
        'schedule': '16:00',  # 4 PM daily
        'extract': ['nifty_levels', 'banknifty_levels', 'strategy_bias']
    },
    'trading_chanakya': {
        'channel_id': 'UC...',  # To be configured
        'extract': ['support_resistance', 'trend_analysis']
    },
    'pr_sundar': {
        'channel_id': 'UC...',  # To be configured
        'extract': ['option_chain_analysis', 'vix_interpretation']
    }
}