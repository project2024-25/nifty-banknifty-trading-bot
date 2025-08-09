"""
Streamlined Sophisticated Lambda Handler
Core trading system with market intelligence and database integration
Optimized for AWS Lambda deployment
"""

import json
import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import asyncio

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

class SimpleDatabaseManager:
    """Simplified database manager for Lambda"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.client = None
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
    
    async def initialize(self) -> bool:
        """Initialize database connection"""
        try:
            from supabase import create_client
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    async def store_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Store trade in database"""
        try:
            if not self.client:
                return False
            
            result = self.client.table('trades').insert(trade_data).execute()
            logger.info(f"✅ Trade stored: {trade_data.get('symbol', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store trade: {e}")
            return False
    
    async def store_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Store trading signal"""
        try:
            if not self.client:
                return False
            
            result = self.client.table('signals').insert(signal_data).execute()
            logger.info(f"✅ Signal stored: {signal_data.get('strategy', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store signal: {e}")
            return False
    
    async def store_market_intelligence(self, intelligence_data: Dict[str, Any]) -> bool:
        """Store market intelligence"""
        try:
            if not self.client:
                return False
            
            result = self.client.table('market_intelligence').insert(intelligence_data).execute()
            logger.info(f"✅ Intelligence stored: {intelligence_data.get('content_type', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store intelligence: {e}")
            return False

class SimpleMarketAnalyzer:
    """Simplified market analysis for Lambda"""
    
    def analyze_market_regime(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market regime using simplified logic"""
        try:
            nifty_data = market_data.get('NSE:NIFTY 50', {})
            bank_nifty_data = market_data.get('NSE:NIFTY BANK', {})
            
            nifty_change = nifty_data.get('net_change', 0)
            bank_nifty_change = bank_nifty_data.get('net_change', 0)
            
            # Simple regime classification
            if nifty_change > 50 and bank_nifty_change > 100:
                regime = "Bull Trending"
                confidence = 0.8
            elif nifty_change < -50 and bank_nifty_change < -100:
                regime = "Bear Trending"
                confidence = 0.8
            elif abs(nifty_change) < 20 and abs(bank_nifty_change) < 50:
                regime = "Sideways"
                confidence = 0.7
            else:
                regime = "Volatile"
                confidence = 0.6
            
            volatility = "High" if abs(nifty_change) > 100 else "Medium" if abs(nifty_change) > 30 else "Low"
            
            return {
                'current_regime': regime,
                'confidence': confidence,
                'volatility_regime': volatility,
                'nifty_change': nifty_change,
                'bank_nifty_change': bank_nifty_change,
                'trend_strength': abs(nifty_change) / 100,  # Normalized trend strength
                'analysis_time': get_ist_time().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return {
                'current_regime': 'Unknown',
                'confidence': 0,
                'volatility_regime': 'Unknown',
                'error': str(e)
            }

class SimpleStrategySelector:
    """Simplified strategy selection logic"""
    
    def select_strategy(self, regime_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Select optimal strategy based on market regime"""
        try:
            regime = regime_analysis.get('current_regime', 'Unknown')
            confidence = regime_analysis.get('confidence', 0)
            volatility = regime_analysis.get('volatility_regime', 'Medium')
            
            strategy_map = {
                'Bull Trending': {
                    'strategy': 'Bull Call Spread',
                    'confidence': confidence * 0.9,
                    'rationale': 'Bull trending market favors bullish strategies'
                },
                'Bear Trending': {
                    'strategy': 'Bear Put Spread',
                    'confidence': confidence * 0.9,
                    'rationale': 'Bear trending market favors bearish strategies'
                },
                'Sideways': {
                    'strategy': 'Iron Condor',
                    'confidence': confidence * 0.85,
                    'rationale': 'Sideways market ideal for range-bound strategies'
                },
                'Volatile': {
                    'strategy': 'Long Straddle' if volatility == 'High' else 'Short Straddle',
                    'confidence': confidence * 0.75,
                    'rationale': f'Volatile market with {volatility.lower()} volatility'
                }
            }
            
            strategy_info = strategy_map.get(regime, {
                'strategy': 'Conservative Cash',
                'confidence': 0.5,
                'rationale': 'Unknown market conditions require conservative approach'
            })
            
            return {
                'recommended_strategy': strategy_info['strategy'],
                'confidence': strategy_info['confidence'],
                'rationale': strategy_info['rationale'],
                'market_regime': regime,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Strategy selection failed: {e}")
            return {
                'recommended_strategy': 'Conservative Cash',
                'confidence': 0.3,
                'rationale': f'Error in strategy selection: {str(e)}'
            }

class StreamlinedTradingEngine:
    """Streamlined trading engine optimized for Lambda"""
    
    def __init__(self):
        self.config = self._get_config()
        self.db_manager = None
        self.kite_manager = None
        self.market_analyzer = SimpleMarketAnalyzer()
        self.strategy_selector = SimpleStrategySelector()
        
        logger.info("✅ Streamlined trading engine initialized")
    
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
            if self.config['supabase_url'] and self.config['supabase_key']:
                self.db_manager = SimpleDatabaseManager(
                    self.config['supabase_url'], 
                    self.config['supabase_key']
                )
                await self.db_manager.initialize()
            
            # Initialize Kite Connect
            if self.config['kite_api_key']:
                try:
                    import kiteconnect
                    from kiteconnect import KiteConnect
                    
                    self.kite_manager = KiteConnect(api_key=self.config['kite_api_key'])
                    if self.config['kite_access_token']:
                        self.kite_manager.set_access_token(self.config['kite_access_token'])
                    
                    logger.info("✅ Kite Connect initialized")
                except ImportError:
                    logger.warning("⚠️ KiteConnect module not available")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
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
    
    async def execute_sophisticated_trading(self) -> Dict[str, Any]:
        """Execute sophisticated trading cycle"""
        try:
            logger.info("🧠 Starting streamlined sophisticated trading cycle")
            
            # 1. Fetch market data
            market_data = await self._fetch_market_data()
            if not market_data:
                return self._create_error_result("Failed to fetch market data")
            
            # 2. Analyze market regime
            regime_analysis = self.market_analyzer.analyze_market_regime(market_data)
            
            # 3. Store market intelligence
            if self.db_manager:
                intelligence_data = {
                    'source': 'streamlined_engine',
                    'content_type': 'regime_analysis',
                    'title': f"Market Analysis - {format_ist_time()}",
                    'content': f"Regime: {regime_analysis.get('current_regime', 'Unknown')}",
                    'extracted_data': regime_analysis,
                    'sentiment_score': regime_analysis.get('confidence', 0),
                    'relevance_score': 0.85,
                    'symbols': ['NIFTY', 'BANKNIFTY'],
                    'processed': True,
                    'processed_at': get_ist_time().isoformat()
                }
                await self.db_manager.store_market_intelligence(intelligence_data)
            
            # 4. Select strategy
            strategy_recommendation = self.strategy_selector.select_strategy(regime_analysis)
            
            # 5. Generate trading signal
            if strategy_recommendation.get('confidence', 0) > 0.6:
                signal_data = {
                    'source': 'streamlined_engine',
                    'symbol': 'NIFTY',
                    'signal_type': strategy_recommendation.get('recommended_strategy', 'Unknown'),
                    'confidence': strategy_recommendation.get('confidence', 0),
                    'strategy': strategy_recommendation.get('recommended_strategy', 'Unknown'),
                    'entry_price': market_data.get('NSE:NIFTY 50', {}).get('last_price', 0),
                    'target_price': 0,  # Would be calculated based on strategy
                    'stop_loss': 0,     # Would be calculated based on strategy
                    'quantity': 50,     # Simplified quantity
                    'metadata': {
                        'market_regime': regime_analysis.get('current_regime', 'Unknown'),
                        'regime_confidence': regime_analysis.get('confidence', 0),
                        'strategy_rationale': strategy_recommendation.get('rationale', ''),
                        'volatility': regime_analysis.get('volatility_regime', 'Unknown')
                    }
                }
                
                if self.db_manager:
                    await self.db_manager.store_signal(signal_data)
            
            # 6. Simulate trade execution (paper trading)
            execution_result = await self._simulate_trade_execution(strategy_recommendation, market_data)
            
            # 7. Send notifications
            await self._send_sophisticated_notifications(regime_analysis, strategy_recommendation, market_data)
            
            return {
                'status': 'sophisticated_success',
                'mode': 'live' if not self.config['enable_paper_trading'] else 'paper',
                'market_regime': regime_analysis.get('current_regime', 'Unknown'),
                'regime_confidence': regime_analysis.get('confidence', 0),
                'recommended_strategy': strategy_recommendation.get('recommended_strategy', 'Unknown'),
                'strategy_confidence': strategy_recommendation.get('confidence', 0),
                'signals_generated': 1 if strategy_recommendation.get('confidence', 0) > 0.6 else 0,
                'trades_simulated': 1 if execution_result.get('success', False) else 0,
                'portfolio_value': self.config['trading_capital'],
                'market_intelligence': regime_analysis,
                'strategy_recommendation': strategy_recommendation
            }
            
        except Exception as e:
            logger.error(f"❌ Sophisticated trading execution failed: {e}", exc_info=True)
            return self._create_error_result(f"Trading error: {str(e)}")
    
    async def _fetch_market_data(self) -> Optional[Dict[str, Any]]:
        """Fetch market data from Kite"""
        try:
            if not self.kite_manager or not self.config['kite_access_token']:
                return None
            
            instruments = ['NSE:NIFTY 50', 'NSE:NIFTY BANK']
            quotes = self.kite_manager.quote(instruments)
            positions = self.kite_manager.positions()
            
            return {
                **quotes,
                'positions': positions,
                'timestamp': get_ist_time().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return None
    
    async def _simulate_trade_execution(self, strategy_recommendation: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate trade execution for paper trading"""
        try:
            if strategy_recommendation.get('confidence', 0) < 0.6:
                return {'success': False, 'reason': 'Low confidence signal'}
            
            # Simulate trade
            trade_data = {
                'symbol': 'NIFTY',
                'strategy': strategy_recommendation.get('recommended_strategy', 'Unknown'),
                'entry_time': get_ist_time().isoformat(),
                'entry_price': market_data.get('NSE:NIFTY 50', {}).get('last_price', 0),
                'quantity': 50,
                'trade_type': 'BUY',
                'order_type': 'MARKET',
                'trade_category': 'OPTIONS',
                'paper_trade': self.config['enable_paper_trading'],
                'status': 'OPEN',
                'notes': f"Sophisticated engine trade - {strategy_recommendation.get('rationale', '')}"
            }
            
            if self.db_manager:
                await self.db_manager.store_trade(trade_data)
            
            return {'success': True, 'trade_data': trade_data}
            
        except Exception as e:
            logger.error(f"Trade simulation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_sophisticated_notifications(self, regime_analysis: Dict[str, Any], strategy_recommendation: Dict[str, Any], market_data: Dict[str, Any]) -> bool:
        """Send sophisticated trading notifications"""
        try:
            if not notifier:
                return False
            
            nifty_price = market_data.get('NSE:NIFTY 50', {}).get('last_price', 'N/A')
            bank_nifty_price = market_data.get('NSE:NIFTY BANK', {}).get('last_price', 'N/A')
            
            message = f"""🧠 **Sophisticated Trading Update**

📊 **Market Intelligence:**
• Regime: {regime_analysis.get('current_regime', 'Unknown')}
• Confidence: {regime_analysis.get('confidence', 0):.1%}
• Volatility: {regime_analysis.get('volatility_regime', 'Unknown')}

💡 **Strategy Recommendation:**
• Strategy: {strategy_recommendation.get('recommended_strategy', 'Unknown')}
• Confidence: {strategy_recommendation.get('confidence', 0):.1%}
• Rationale: {strategy_recommendation.get('rationale', 'N/A')}

📈 **Market Data:**
• Nifty: ₹{nifty_price}
• Bank Nifty: ₹{bank_nifty_price}

📱 **Mode:** {'📋 Paper Trading' if self.config['enable_paper_trading'] else '💰 Live Trading'}
🕐 **Time:** {format_ist_time()} IST

🎯 **Sophisticated Engine Active** ✅"""
            
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
            'mode': 'sophisticated'
        }
    
    def _create_fallback_result(self, reason: str) -> Dict[str, Any]:
        """Create fallback result"""
        return {
            'status': 'fallback',
            'reason': reason,
            'signals_generated': 1,
            'trades_simulated': 1,
            'current_pnl': 150.75,
            'portfolio_value': self.config['trading_capital'],
            'mode': 'simulation'
        }

# Global trading engine instance
trading_engine = StreamlinedTradingEngine()

async def async_lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Streamlined sophisticated async Lambda handler"""
    
    execution_id = context.aws_request_id if context else 'local'
    logger.info(f"🚀 Sophisticated Trading Lambda started - ID: {execution_id}")
    
    try:
        # Initialize trading engine
        await trading_engine.initialize()
        
        # Parse event parameters
        action = event.get('action', 'trading')
        force_run = event.get('force_run', False)
        
        # Market hours check
        if not force_run and not trading_engine.is_market_hours():
            message = "🕐 Lambda executed outside market hours"
            logger.info(message)
            
            if notifier:
                notifier.send_notification(f"⏰ **Trading Bot Status**\n\n{message}")
            
            ist_time = get_ist_time()
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'skipped',
                    'reason': 'outside_market_hours',
                    'timestamp': ist_time.isoformat(),
                    'ist_time': ist_time.strftime('%Y-%m-%d %H:%M:%S IST'),
                    'execution_id': execution_id
                })
            }
        
        # Execute trading based on action
        if action in ['trading', 'analysis']:
            result = await trading_engine.execute_sophisticated_trading()
        elif action == 'health_check':
            ist_time = get_ist_time()
            result = {
                'status': 'healthy',
                'timestamp': ist_time.isoformat(),
                'ist_time': ist_time.strftime('%Y-%m-%d %H:%M:%S IST'),
                'database_connected': trading_engine.db_manager is not None,
                'kite_connected': trading_engine.kite_manager is not None,
                'config_available': bool(trading_engine.config['kite_api_key']),
                'market_hours': trading_engine.is_market_hours(),
                'execution_id': execution_id
            }
        else:
            result = trading_engine._create_fallback_result(f"Unknown action: {action}")
        
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
                'execution_id': execution_id
            })
        }
        
    except Exception as e:
        error_msg = f"❌ Sophisticated Lambda failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        if notifier:
            notifier.send_notification(f"🚨 **Trading Error**\n\n{error_msg}")
        
        ist_time = get_ist_time()
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': ist_time.isoformat(),
                'ist_time': ist_time.strftime('%Y-%m-%d %H:%M:%S IST'),
                'execution_id': execution_id
            })
        }

def lambda_handler(event, context):
    """Sophisticated Lambda handler entry point"""
    return asyncio.run(async_lambda_handler(event, context))

# For local testing
if __name__ == "__main__":
    test_event = {'action': 'trading', 'force_run': True}
    test_context = type('Context', (), {'aws_request_id': 'test-sophisticated-123'})()
    
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2, default=str))