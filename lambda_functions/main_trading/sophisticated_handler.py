"""
Full Sophisticated Lambda Handler
Complete trading system with market intelligence, strategy selection, and database integration
"""

import json
import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import asyncio
import traceback

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_time():
    """Get current time in IST."""
    return datetime.now(IST)

def format_ist_time(dt_format='%Y-%m-%d %H:%M:%S'):
    """Format current IST time."""
    return get_ist_time().strftime(dt_format)

# Import telegram helper
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from telegram_helper import SimpleTelegramNotifier
    notifier = SimpleTelegramNotifier()
    logger.info("✅ Telegram notifier imported successfully")
except ImportError as e:
    notifier = None
    logger.warning(f"⚠️ Telegram notifier not available: {e}")

# Import sophisticated components with fallbacks
try:
    # Add source paths for sophisticated components
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, current_dir)
    
    # Try importing sophisticated modules
    from src.integrations.database import DatabaseManager
    from src.intelligence.market_regime import MarketRegimeDetector
    from src.intelligence.strategy_selector import AdaptiveStrategySelector
    from src.intelligence.dynamic_allocator import DynamicAllocationManager, AllocationMode
    from src.intelligence.dashboard_simple import SimpleMarketDashboard
    
    SOPHISTICATED_MODE = True
    logger.info("✅ Full sophisticated components imported successfully")
    
except ImportError as import_error:
    logger.warning(f"⚠️ Sophisticated components not available: {import_error}")
    SOPHISTICATED_MODE = False

# Fallback simplified components for when sophisticated imports fail
if not SOPHISTICATED_MODE:
    class DatabaseManager:
        def __init__(self): 
            self.client = None
            self.supabase_url = os.getenv('SUPABASE_URL', '')
            self.supabase_key = os.getenv('SUPABASE_KEY', '')
        
        async def initialize(self):
            try:
                from supabase import create_client, Client
                if self.supabase_url and self.supabase_key:
                    self.client = create_client(self.supabase_url, self.supabase_key)
                    logger.info("✅ Fallback database initialized")
                    return True
            except Exception as e:
                logger.error(f"❌ Database initialization failed: {e}")
            return False
        
        async def create_trade(self, trade_data):
            if self.client:
                try:
                    result = self.client.table('trades').insert(trade_data).execute()
                    return result.data[0]['id'] if result.data else None
                except Exception as e:
                    logger.error(f"Failed to create trade: {e}")
            return None
        
        async def create_signal(self, signal_data):
            if self.client:
                try:
                    result = self.client.table('signals').insert(signal_data).execute()
                    return result.data[0]['id'] if result.data else None
                except Exception as e:
                    logger.error(f"Failed to create signal: {e}")
            return None
        
        async def store_intelligence(self, intelligence_data):
            if self.client:
                try:
                    result = self.client.table('market_intelligence').insert(intelligence_data).execute()
                    return result.data[0]['id'] if result.data else None
                except Exception as e:
                    logger.error(f"Failed to store intelligence: {e}")
            return None
    
    class MarketRegimeDetector:
        def detect_regime(self, market_data):
            """Fallback market regime detection"""
            try:
                # Simple regime detection based on price changes
                nifty_data = market_data.get('quotes', {}).get('NSE:NIFTY 50', {})
                bank_nifty_data = market_data.get('quotes', {}).get('NSE:NIFTY BANK', {})
                
                nifty_change = nifty_data.get('net_change', 0)
                bank_nifty_change = bank_nifty_data.get('net_change', 0)
                
                if nifty_change > 50 and bank_nifty_change > 100:
                    return {
                        'regime': 'Bull Trending',
                        'confidence': 0.8,
                        'volatility_regime': 'Medium',
                        'trend_strength': abs(nifty_change) / 100
                    }
                elif nifty_change < -50 and bank_nifty_change < -100:
                    return {
                        'regime': 'Bear Trending', 
                        'confidence': 0.8,
                        'volatility_regime': 'Medium',
                        'trend_strength': abs(nifty_change) / 100
                    }
                elif abs(nifty_change) < 20:
                    return {
                        'regime': 'Sideways',
                        'confidence': 0.7,
                        'volatility_regime': 'Low',
                        'trend_strength': 0.2
                    }
                else:
                    return {
                        'regime': 'Volatile',
                        'confidence': 0.6,
                        'volatility_regime': 'High',
                        'trend_strength': abs(nifty_change) / 100
                    }
            except Exception as e:
                logger.error(f"Regime detection failed: {e}")
                return {'regime': 'Unknown', 'confidence': 0, 'error': str(e)}
    
    class AdaptiveStrategySelector:
        async def select_strategies(self, market_data, regime_analysis):
            """Fallback strategy selection"""
            regime = regime_analysis.get('regime', 'Unknown')
            confidence = regime_analysis.get('confidence', 0)
            
            strategies = {
                'Bull Trending': {
                    'Bull Call Spread': {
                        'confidence': confidence * 0.9,
                        'allocation': 0.4,
                        'rationale': 'Bullish market favors call spreads'
                    }
                },
                'Bear Trending': {
                    'Bear Put Spread': {
                        'confidence': confidence * 0.9,
                        'allocation': 0.4,
                        'rationale': 'Bearish market favors put spreads'
                    }
                },
                'Sideways': {
                    'Iron Condor': {
                        'confidence': confidence * 0.85,
                        'allocation': 0.3,
                        'rationale': 'Range-bound market ideal for condors'
                    }
                },
                'Volatile': {
                    'Long Straddle': {
                        'confidence': confidence * 0.75,
                        'allocation': 0.3,
                        'rationale': 'High volatility favors straddles'
                    }
                }
            }
            
            return strategies.get(regime, {
                'Conservative': {
                    'confidence': 0.5,
                    'allocation': 0.1,
                    'rationale': 'Unknown conditions require caution'
                }
            })

class FullSophisticatedTradingEngine:
    """Full sophisticated trading engine with all features"""
    
    def __init__(self):
        self.config = self._get_config()
        self.db_manager = None
        self.kite_manager = None
        self.sophisticated_mode = SOPHISTICATED_MODE
        
        # Initialize sophisticated components
        if SOPHISTICATED_MODE:
            try:
                self.regime_detector = MarketRegimeDetector()
                self.strategy_selector = AdaptiveStrategySelector()
                self.allocation_manager = DynamicAllocationManager(
                    total_capital=self.config['trading_capital']
                )
                self.dashboard = SimpleMarketDashboard(
                    capital=self.config['trading_capital']
                )
                logger.info("✅ Full sophisticated components initialized")
            except Exception as e:
                logger.error(f"❌ Sophisticated component initialization failed: {e}")
                self.sophisticated_mode = False
        
        if not self.sophisticated_mode:
            # Fallback components
            self.regime_detector = MarketRegimeDetector()
            self.strategy_selector = AdaptiveStrategySelector()
            logger.info("⚡ Fallback components initialized")
        
        self.db_manager = DatabaseManager()
    
    def _get_config(self) -> Dict[str, Any]:
        """Get configuration from environment variables."""
        return {
            'kite_api_key': os.getenv('KITE_API_KEY', ''),
            'kite_api_secret': os.getenv('KITE_API_SECRET', ''),
            'kite_access_token': os.getenv('KITE_ACCESS_TOKEN', ''),
            'supabase_url': os.getenv('SUPABASE_URL', ''),
            'supabase_key': os.getenv('SUPABASE_KEY', ''),
            'enable_paper_trading': os.getenv('ENABLE_PAPER_TRADING', 'true').lower() == 'true',
            'trading_capital': float(os.getenv('TRADING_CAPITAL', '1000000')),
            'telegram_user_id': int(os.getenv('TELEGRAM_USER_ID', '0')),
            'max_daily_loss_percent': float(os.getenv('MAX_DAILY_LOSS_PERCENT', '3'))
        }
    
    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Initialize database
            if self.db_manager and self.config['supabase_url']:
                db_success = await self.db_manager.initialize()
                if db_success:
                    logger.info("✅ Database connection established")
                else:
                    logger.warning("⚠️ Database connection failed")
            
            # Initialize Kite Connect
            if self.config['kite_api_key']:
                try:
                    import kiteconnect
                    from kiteconnect import KiteConnect
                    
                    self.kite_manager = KiteConnect(api_key=self.config['kite_api_key'])
                    if self.config['kite_access_token']:
                        self.kite_manager.set_access_token(self.config['kite_access_token'])
                    
                    # Test connection
                    profile = self.kite_manager.profile()
                    logger.info(f"✅ Kite Connect initialized for user: {profile.get('user_name', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"❌ Kite Connect initialization failed: {e}")
                    self.kite_manager = None
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Engine initialization failed: {e}")
            return False
    
    def is_market_hours(self) -> bool:
        """Check if current time is within market hours (9:15 AM - 3:30 PM IST)."""
        try:
            now = get_ist_time()
            
            # Skip weekends
            if now.weekday() >= 5:
                return False
            
            # Market hours: 9:15 AM to 3:30 PM IST
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
            
            return market_open <= now <= market_close
            
        except Exception as e:
            logger.error(f"Error checking market hours: {e}")
            return False
    
    async def execute_full_sophisticated_cycle(self) -> Dict[str, Any]:
        """Execute complete sophisticated trading cycle"""
        try:
            logger.info(f"🧠 Starting {'FULL' if self.sophisticated_mode else 'FALLBACK'} sophisticated trading cycle")
            
            # 1. Fetch comprehensive market data
            market_data = await self._fetch_comprehensive_market_data()
            if not market_data:
                return self._create_error_result("Failed to fetch market data")
            
            # 2. Perform market regime analysis
            regime_analysis = self.regime_detector.detect_regime(market_data)
            logger.info(f"📊 Market regime: {regime_analysis.get('regime', 'Unknown')} (confidence: {regime_analysis.get('confidence', 0):.1%})")
            
            # 3. Store market intelligence in database
            if self.db_manager:
                intelligence_data = {
                    'source': 'sophisticated_trading_engine',
                    'content_type': 'regime_analysis',
                    'title': f"Market Analysis - {format_ist_time()}",
                    'content': f"Market Regime: {regime_analysis.get('regime', 'Unknown')}",
                    'extracted_data': regime_analysis,
                    'sentiment_score': regime_analysis.get('confidence', 0),
                    'relevance_score': 0.95,
                    'symbols': ['NIFTY', 'BANKNIFTY'],
                    'processed': True,
                    'processed_at': get_ist_time().isoformat()
                }
                await self.db_manager.store_intelligence(intelligence_data)
            
            # 4. Generate adaptive strategy signals
            strategy_recommendations = await self.strategy_selector.select_strategies(market_data, regime_analysis)
            
            # 5. Process each recommended strategy
            signals_generated = 0
            trades_executed = 0
            
            for strategy_name, strategy_info in strategy_recommendations.items():
                if strategy_info.get('confidence', 0) > 0.6:
                    # Generate signal
                    signal_data = {
                        'source': 'sophisticated_engine',
                        'symbol': 'NIFTY',
                        'signal_type': strategy_name,
                        'confidence': strategy_info.get('confidence', 0),
                        'strategy': strategy_name,
                        'entry_price': market_data.get('quotes', {}).get('NSE:NIFTY 50', {}).get('last_price', 0),
                        'target_price': 0,  # Would be calculated by strategy
                        'stop_loss': 0,     # Would be calculated by strategy
                        'quantity': int(strategy_info.get('allocation', 0.1) * 100),
                        'metadata': {
                            'market_regime': regime_analysis.get('regime', 'Unknown'),
                            'regime_confidence': regime_analysis.get('confidence', 0),
                            'strategy_rationale': strategy_info.get('rationale', ''),
                            'volatility': regime_analysis.get('volatility_regime', 'Unknown')
                        }
                    }
                    
                    if self.db_manager:
                        signal_id = await self.db_manager.create_signal(signal_data)
                        if signal_id:
                            signals_generated += 1
                    
                    # Simulate trade execution for paper trading
                    if self.config['enable_paper_trading']:
                        trade_data = {
                            'symbol': 'NIFTY',
                            'strategy': strategy_name,
                            'entry_time': get_ist_time().isoformat(),
                            'entry_price': signal_data['entry_price'],
                            'quantity': signal_data['quantity'],
                            'trade_type': 'BUY',
                            'order_type': 'MARKET',
                            'trade_category': 'OPTIONS',
                            'paper_trade': True,
                            'status': 'OPEN',
                            'notes': f"Sophisticated engine: {strategy_info.get('rationale', '')}"
                        }
                        
                        if self.db_manager:
                            trade_id = await self.db_manager.create_trade(trade_data)
                            if trade_id:
                                trades_executed += 1
            
            # 6. Send sophisticated notifications
            await self._send_full_sophisticated_notifications(
                regime_analysis, 
                strategy_recommendations, 
                market_data,
                signals_generated,
                trades_executed
            )
            
            # 7. Return comprehensive results
            return {
                'status': 'full_sophisticated_success',
                'mode': f"{'FULL' if self.sophisticated_mode else 'FALLBACK'}_SOPHISTICATED",
                'trading_mode': 'paper' if self.config['enable_paper_trading'] else 'live',
                'market_regime': regime_analysis.get('regime', 'Unknown'),
                'regime_confidence': regime_analysis.get('confidence', 0),
                'volatility_regime': regime_analysis.get('volatility_regime', 'Unknown'),
                'trend_strength': regime_analysis.get('trend_strength', 0),
                'strategies_recommended': len(strategy_recommendations),
                'signals_generated': signals_generated,
                'trades_executed': trades_executed,
                'portfolio_value': self.config['trading_capital'],
                'database_connected': self.db_manager.client is not None if self.db_manager else False,
                'kite_connected': self.kite_manager is not None,
                'market_intelligence': regime_analysis,
                'strategy_recommendations': strategy_recommendations
            }
            
        except Exception as e:
            error_msg = f"Full sophisticated cycle failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self._create_error_result(error_msg)
    
    async def _fetch_comprehensive_market_data(self) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive market data"""
        try:
            if not self.kite_manager or not self.config['kite_access_token']:
                logger.warning("Kite manager not available, using mock data")
                return {
                    'quotes': {
                        'NSE:NIFTY 50': {'last_price': 24500, 'net_change': 25},
                        'NSE:NIFTY BANK': {'last_price': 52000, 'net_change': 150}
                    },
                    'positions': {'net': []},
                    'timestamp': get_ist_time().isoformat()
                }
            
            # Fetch real market data
            instruments = ['NSE:NIFTY 50', 'NSE:NIFTY BANK', 'NSE:NIFTY FIN SERVICE']
            quotes = self.kite_manager.quote(instruments)
            positions = self.kite_manager.positions()
            
            return {
                'quotes': quotes,
                'positions': positions,
                'timestamp': get_ist_time().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return None
    
    async def _send_full_sophisticated_notifications(self, regime_analysis, strategy_recommendations, market_data, signals_generated, trades_executed):
        """Send comprehensive sophisticated notifications"""
        try:
            if not notifier:
                return False
            
            nifty_data = market_data.get('quotes', {}).get('NSE:NIFTY 50', {})
            bank_nifty_data = market_data.get('quotes', {}).get('NSE:NIFTY BANK', {})
            
            # Get top strategy recommendation
            top_strategy = max(strategy_recommendations.items(), key=lambda x: x[1].get('confidence', 0)) if strategy_recommendations else ('None', {})
            
            message = f"""🧠 **FULL SOPHISTICATED TRADING SYSTEM**

📊 **Market Intelligence:**
• Regime: {regime_analysis.get('regime', 'Unknown')} ({regime_analysis.get('confidence', 0):.1%} confidence)
• Volatility: {regime_analysis.get('volatility_regime', 'Unknown')}
• Trend Strength: {regime_analysis.get('trend_strength', 0):.2f}

💡 **Strategy Engine:**
• Top Strategy: {top_strategy[0]}
• Strategy Confidence: {top_strategy[1].get('confidence', 0):.1%}
• Rationale: {top_strategy[1].get('rationale', 'N/A')}

📈 **Market Data:**
• Nifty: ₹{nifty_data.get('last_price', 'N/A')} ({nifty_data.get('net_change', 0):+.1f})
• Bank Nifty: ₹{bank_nifty_data.get('last_price', 'N/A')} ({bank_nifty_data.get('net_change', 0):+.1f})

⚡ **Execution Summary:**
• Strategies Analyzed: {len(strategy_recommendations)}
• Signals Generated: {signals_generated}
• Trades Executed: {trades_executed}
• Mode: {'📋 Paper Trading' if self.config['enable_paper_trading'] else '💰 Live Trading'}

🎯 **System Status:**
• Engine: {'FULL SOPHISTICATED' if self.sophisticated_mode else 'FALLBACK SOPHISTICATED'}
• Database: {'✅ Connected' if self.db_manager and self.db_manager.client else '❌ Disconnected'}
• Kite API: {'✅ Connected' if self.kite_manager else '❌ Disconnected'}

🕐 **Time:** {format_ist_time()} IST

🚀 **Your Enterprise Trading System is Active!**"""
            
            return notifier.send_notification(message)
            
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
            return False
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            'status': 'error',
            'error': error_message,
            'timestamp': get_ist_time().isoformat(),
            'mode': f"{'FULL' if self.sophisticated_mode else 'FALLBACK'}_SOPHISTICATED"
        }

# Global trading engine instance
trading_engine = FullSophisticatedTradingEngine()

async def async_lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Full sophisticated async Lambda handler"""
    
    execution_id = context.aws_request_id if context else 'local'
    logger.info(f"🚀 FULL SOPHISTICATED Trading Lambda started - ID: {execution_id}")
    
    try:
        # Initialize trading engine
        initialization_success = await trading_engine.initialize()
        if not initialization_success:
            logger.warning("⚠️ Partial initialization, continuing with available components")
        
        # Parse event parameters
        action = event.get('action', 'trading')
        force_run = event.get('force_run', False)
        
        # Market hours check
        if not force_run and not trading_engine.is_market_hours():
            message = "🕐 Lambda executed outside market hours"
            logger.info(message)
            
            if notifier:
                notifier.send_notification(f"⏰ **Sophisticated Trading Status**\n\n{message}")
            
            ist_time = get_ist_time()
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'skipped',
                    'reason': 'outside_market_hours',
                    'timestamp': ist_time.isoformat(),
                    'ist_time': ist_time.strftime('%Y-%m-%d %H:%M:%S IST'),
                    'execution_id': execution_id,
                    'sophisticated_mode': trading_engine.sophisticated_mode
                })
            }
        
        # Execute trading based on action
        if action in ['trading', 'analysis']:
            result = await trading_engine.execute_full_sophisticated_cycle()
        elif action == 'health_check':
            ist_time = get_ist_time()
            result = {
                'status': 'healthy',
                'timestamp': ist_time.isoformat(),
                'ist_time': ist_time.strftime('%Y-%m-%d %H:%M:%S IST'),
                'sophisticated_mode': trading_engine.sophisticated_mode,
                'database_connected': trading_engine.db_manager.client is not None if trading_engine.db_manager else False,
                'kite_connected': trading_engine.kite_manager is not None,
                'config_available': bool(trading_engine.config['kite_api_key']),
                'market_hours': trading_engine.is_market_hours(),
                'execution_id': execution_id
            }
        else:
            result = {
                'status': 'fallback',
                'reason': f'Unknown action: {action}',
                'timestamp': get_ist_time().isoformat()
            }
        
        # Success response
        ist_time = get_ist_time()
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'action': action,
                'result': result,
                'timestamp': ist_time.isoformat(),
                'ist_time': ist_time.strftime('%Y-%m-%d %H:%M:%S IST'),
                'execution_id': execution_id,
                'sophisticated_mode': trading_engine.sophisticated_mode
            })
        }
        
    except Exception as e:
        error_msg = f"❌ Full Sophisticated Lambda failed: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        if notifier:
            notifier.send_notification(f"🚨 **Sophisticated Trading Error**\n\n{error_msg}")
        
        ist_time = get_ist_time()
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': ist_time.isoformat(),
                'ist_time': ist_time.strftime('%Y-%m-%d %H:%M:%S IST'),
                'execution_id': execution_id,
                'sophisticated_mode': getattr(trading_engine, 'sophisticated_mode', False)
            })
        }

def lambda_handler(event, context):
    """Full sophisticated Lambda handler entry point"""
    return asyncio.run(async_lambda_handler(event, context))

# For local testing
if __name__ == "__main__":
    test_event = {'action': 'trading', 'force_run': True}
    test_context = type('Context', (), {'aws_request_id': 'test-full-sophisticated-123'})()
    
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2, default=str))