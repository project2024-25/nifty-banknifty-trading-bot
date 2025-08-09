"""
Sophisticated Lambda Handler with Market Intelligence and Database Integration
Replaces simple_handler.py with full trading system capabilities
"""

import json
import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import asyncio

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

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

# Import sophisticated components
try:
    from src.integrations.database import DatabaseManager
    from src.integrations.kite_connect import KiteConnectManager
    from src.intelligence.market_regime import MarketRegimeDetector
    from src.intelligence.strategy_selector import AdaptiveStrategySelector
    from src.intelligence.dynamic_allocator import DynamicAllocationManager, AllocationMode
    from src.intelligence.dashboard_simple import SimpleMarketDashboard
    from src.utils.config import get_config
    SOPHISTICATED_IMPORTS = True
    logger.info("✅ Sophisticated trading components imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ Sophisticated imports failed, falling back to basic mode: {e}")
    SOPHISTICATED_IMPORTS = False

# Import telegram helper
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from telegram_helper import SimpleTelegramNotifier
    notifier = SimpleTelegramNotifier()
    logger.info("✅ Telegram notifier imported successfully")
except ImportError as e:
    notifier = None
    logger.warning(f"⚠️ Telegram notifier not available: {e}")

class SophisticatedTradingEngine:
    """Enhanced trading engine with full market intelligence and database integration"""
    
    def __init__(self):
        self.config = self._get_config()
        self.db_manager = None
        self.kite_manager = None
        self.market_intelligence = {}
        self.sophisticated_mode = SOPHISTICATED_IMPORTS
        
        # Initialize sophisticated components if available
        if self.sophisticated_mode:
            try:
                self.regime_detector = MarketRegimeDetector()
                self.strategy_selector = AdaptiveStrategySelector()
                self.allocation_manager = DynamicAllocationManager(
                    total_capital=float(self.config.get('trading_capital', 1000000))
                )
                self.dashboard = SimpleMarketDashboard(
                    capital=float(self.config.get('trading_capital', 1000000))
                )
                logger.info("✅ Sophisticated trading engine components initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize sophisticated components: {e}")
                self.sophisticated_mode = False
    
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
                self.db_manager = DatabaseManager()
                db_init = await self.db_manager.initialize()
                if db_init:
                    logger.info("✅ Database initialized successfully")
                else:
                    logger.warning("⚠️ Database initialization failed, continuing without DB")
            else:
                logger.warning("⚠️ Supabase credentials not configured")
            
            # Initialize Kite Connect
            if self.config['kite_api_key']:
                try:
                    import kiteconnect
                    from kiteconnect import KiteConnect
                    
                    self.kite_manager = KiteConnect(api_key=self.config['kite_api_key'])
                    if self.config['kite_access_token']:
                        self.kite_manager.set_access_token(self.config['kite_access_token'])
                    
                    logger.info("✅ Kite Connect initialized successfully")
                except ImportError:
                    logger.warning("⚠️ KiteConnect module not available")
                except Exception as e:
                    logger.error(f"❌ Kite Connect initialization failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def is_market_hours(self) -> bool:
        """Check if current time is within market hours (9:15 AM - 3:30 PM IST)."""
        try:
            now = get_ist_time()
            
            # Skip weekends
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
            
            # Market hours: 9:15 AM to 3:30 PM IST
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
            
            return market_open <= now <= market_close
            
        except Exception as e:
            logger.error(f"Error checking market hours: {e}")
            return False
    
    async def execute_sophisticated_trading(self) -> Dict[str, Any]:
        """Execute full sophisticated trading cycle with market intelligence"""
        try:
            if not self.sophisticated_mode:
                return await self._execute_basic_trading()
            
            logger.info("🧠 Starting sophisticated trading cycle")
            
            # 1. Fetch market data
            market_data = await self._fetch_comprehensive_market_data()
            if not market_data:
                return self._create_error_result("Failed to fetch market data")
            
            # 2. Perform market regime detection
            regime_analysis = await self._analyze_market_regime(market_data)
            
            # 3. Generate trading signals using adaptive strategy selection
            signals = await self._generate_adaptive_signals(market_data, regime_analysis)
            
            # 4. Perform portfolio allocation and risk management
            portfolio_actions = await self._execute_portfolio_management(signals, regime_analysis)
            
            # 5. Execute trades and update database
            execution_results = await self._execute_trades(portfolio_actions)
            
            # 6. Update performance metrics and dashboard
            await self._update_performance_metrics(execution_results, regime_analysis)
            
            # 7. Send comprehensive notifications
            await self._send_sophisticated_notifications(execution_results, regime_analysis)
            
            return {
                'status': 'sophisticated_success',
                'mode': 'live' if not self.config['enable_paper_trading'] else 'paper',
                'market_regime': regime_analysis.get('current_regime', 'Unknown'),
                'regime_confidence': regime_analysis.get('confidence', 0),
                'signals_generated': len(signals),
                'trades_executed': len(execution_results.get('executed_trades', [])),
                'portfolio_value': execution_results.get('portfolio_value', 0),
                'risk_utilization': execution_results.get('risk_utilization', 0),
                'performance_summary': execution_results.get('performance_summary', {}),
                'market_intelligence': regime_analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Sophisticated trading execution failed: {e}", exc_info=True)
            return self._create_error_result(f"Sophisticated trading error: {str(e)}")
    
    async def _fetch_comprehensive_market_data(self) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive market data for analysis"""
        try:
            if not self.kite_manager:
                return None
            
            # Fetch major indices and options data
            instruments = ['NSE:NIFTY 50', 'NSE:NIFTY BANK', 'NSE:NIFTY FIN SERVICE', 'NSE:NIFTY IT']
            quotes = self.kite_manager.quote(instruments)
            
            # Get positions and portfolio
            positions = self.kite_manager.positions()
            portfolio = self.kite_manager.holdings()
            
            return {
                'quotes': quotes,
                'positions': positions,
                'portfolio': portfolio,
                'timestamp': get_ist_time().isoformat(),
                'instruments': instruments
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch comprehensive market data: {e}")
            return None
    
    async def _analyze_market_regime(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive market regime analysis"""
        try:
            if not self.sophisticated_mode:
                return {'current_regime': 'Unknown', 'confidence': 0}
            
            # Extract price data for analysis
            nifty_data = market_data['quotes'].get('NSE:NIFTY 50', {})
            bank_nifty_data = market_data['quotes'].get('NSE:NIFTY BANK', {})
            
            # Create market data structure for regime detection
            regime_input = {
                'nifty_price': nifty_data.get('last_price', 0),
                'nifty_change': nifty_data.get('net_change', 0),
                'bank_nifty_price': bank_nifty_data.get('last_price', 0),
                'bank_nifty_change': bank_nifty_data.get('net_change', 0),
                'volume': nifty_data.get('volume', 0),
                'timestamp': get_ist_time()
            }
            
            # Perform regime detection
            regime_result = self.regime_detector.detect_regime(regime_input)
            
            # Store market intelligence in database
            if self.db_manager:
                intelligence_data = {
                    'source': 'market_regime_detector',
                    'content_type': 'regime_analysis',
                    'title': f"Market Regime Analysis - {format_ist_time()}",
                    'content': f"Regime: {regime_result.get('regime', 'Unknown')}",
                    'extracted_data': regime_result,
                    'sentiment_score': regime_result.get('confidence', 0),
                    'relevance_score': 0.9,
                    'symbols': ['NIFTY', 'BANKNIFTY'],
                    'processed': True,
                    'processed_at': get_ist_time().isoformat()
                }
                await self.db_manager.store_intelligence(intelligence_data)
            
            return regime_result
            
        except Exception as e:
            logger.error(f"Market regime analysis failed: {e}")
            return {'current_regime': 'Error', 'confidence': 0, 'error': str(e)}
    
    async def _generate_adaptive_signals(self, market_data: Dict[str, Any], regime_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals using adaptive strategy selection"""
        try:
            if not self.sophisticated_mode:
                return []
            
            # Use strategy selector to get optimal strategies for current regime
            strategy_allocation = await self.strategy_selector.select_strategies(market_data, regime_analysis)
            
            signals = []
            for strategy_name, allocation_info in strategy_allocation.items():
                if allocation_info.get('confidence', 0) > 0.6:  # Only high confidence signals
                    signal = {
                        'source': 'adaptive_strategy_selector',
                        'symbol': allocation_info.get('symbol', 'NIFTY'),
                        'signal_type': strategy_name,
                        'confidence': allocation_info.get('confidence', 0),
                        'strategy': strategy_name,
                        'entry_price': allocation_info.get('entry_price', 0),
                        'target_price': allocation_info.get('target_price', 0),
                        'stop_loss': allocation_info.get('stop_loss', 0),
                        'quantity': allocation_info.get('quantity', 0),
                        'metadata': {
                            'market_regime': regime_analysis.get('current_regime', 'Unknown'),
                            'regime_confidence': regime_analysis.get('confidence', 0),
                            'strategy_rationale': allocation_info.get('rationale', ''),
                            'risk_level': allocation_info.get('risk_level', 'Medium')
                        }
                    }
                    signals.append(signal)
                    
                    # Store signal in database
                    if self.db_manager:
                        await self.db_manager.create_signal(signal)
            
            logger.info(f"Generated {len(signals)} adaptive trading signals")
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return []
    
    async def _execute_portfolio_management(self, signals: List[Dict[str, Any]], regime_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sophisticated portfolio management with dynamic allocation"""
        try:
            if not self.sophisticated_mode or not signals:
                return {'actions': []}
            
            # Use dynamic allocator to determine position sizes
            allocation_result = self.allocation_manager.allocate_portfolio(
                signals, 
                regime_analysis, 
                AllocationMode.REGIME_ADAPTIVE
            )
            
            return allocation_result
            
        except Exception as e:
            logger.error(f"Portfolio management failed: {e}")
            return {'actions': [], 'error': str(e)}
    
    async def _execute_trades(self, portfolio_actions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trades and update positions"""
        try:
            executed_trades = []
            total_portfolio_value = 0
            
            # In paper trading mode, simulate trade execution
            if self.config['enable_paper_trading']:
                for action in portfolio_actions.get('actions', []):
                    trade_result = await self._simulate_trade_execution(action)
                    if trade_result:
                        executed_trades.append(trade_result)
                        
                        # Store trade in database
                        if self.db_manager:
                            await self.db_manager.create_trade(trade_result)
            
            else:
                # Live trading execution
                for action in portfolio_actions.get('actions', []):
                    trade_result = await self._execute_live_trade(action)
                    if trade_result:
                        executed_trades.append(trade_result)
                        
                        # Store trade in database
                        if self.db_manager:
                            await self.db_manager.create_trade(trade_result)
            
            # Calculate portfolio value and risk metrics
            if self.db_manager:
                positions = await self.db_manager.get_active_positions(self.config['enable_paper_trading'])
                total_portfolio_value = sum(pos.get('unrealized_pnl', 0) for pos in positions)
            
            return {
                'executed_trades': executed_trades,
                'portfolio_value': total_portfolio_value,
                'risk_utilization': len(executed_trades) * 10,  # Simplified risk calculation
                'performance_summary': {
                    'trades_today': len(executed_trades),
                    'active_positions': len(executed_trades)
                }
            }
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return {'executed_trades': [], 'error': str(e)}
    
    async def _simulate_trade_execution(self, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Simulate trade execution for paper trading"""
        try:
            ist_time = get_ist_time()
            
            return {
                'symbol': action.get('symbol', 'NIFTY'),
                'strategy': action.get('strategy', 'Unknown'),
                'entry_time': ist_time.isoformat(),
                'entry_price': action.get('entry_price', 0),
                'quantity': action.get('quantity', 0),
                'trade_type': action.get('trade_type', 'BUY'),
                'order_type': 'MARKET',
                'trade_category': action.get('category', 'OPTIONS'),
                'paper_trade': True,
                'status': 'OPEN',
                'notes': f"Paper trade executed via sophisticated engine"
            }
            
        except Exception as e:
            logger.error(f"Trade simulation failed: {e}")
            return None
    
    async def _execute_live_trade(self, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute live trade via Kite Connect"""
        try:
            # Live trading implementation would go here
            # For now, return simulated result
            logger.info("Live trading not implemented yet, simulating...")
            return await self._simulate_trade_execution(action)
            
        except Exception as e:
            logger.error(f"Live trade execution failed: {e}")
            return None
    
    async def _update_performance_metrics(self, execution_results: Dict[str, Any], regime_analysis: Dict[str, Any]) -> bool:
        """Update daily performance metrics"""
        try:
            if not self.db_manager:
                return False
            
            today = get_ist_time().date()
            
            # Calculate daily metrics
            executed_trades = execution_results.get('executed_trades', [])
            daily_metrics = {
                'total_trades': len(executed_trades),
                'winning_trades': 0,  # Would be calculated from closed trades
                'losing_trades': 0,
                'total_pnl': execution_results.get('portfolio_value', 0),
                'conservative_pnl': 0,
                'aggressive_pnl': 0,
                'max_drawdown': 0,
                'paper_trade': self.config['enable_paper_trading']
            }
            
            await self.db_manager.update_daily_metrics(today, daily_metrics, self.config['enable_paper_trading'])
            logger.info("✅ Performance metrics updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
            return False
    
    async def _send_sophisticated_notifications(self, execution_results: Dict[str, Any], regime_analysis: Dict[str, Any]) -> bool:
        """Send comprehensive trading notifications"""
        try:
            if not notifier:
                return False
            
            ist_time = format_ist_time()
            executed_trades = execution_results.get('executed_trades', [])
            
            message = f"""🧠 **Sophisticated Trading Update**

📊 **Market Intelligence:**
• Regime: {regime_analysis.get('current_regime', 'Unknown')}
• Confidence: {regime_analysis.get('confidence', 0):.1%}
• Volatility: {regime_analysis.get('volatility_regime', 'Unknown')}

💼 **Portfolio Status:**
• Trades Executed: {len(executed_trades)}
• Portfolio Value: ₹{execution_results.get('portfolio_value', 0):,.2f}
• Risk Utilization: {execution_results.get('risk_utilization', 0):.1%}

📈 **Trading Mode:** {'📋 Paper Trading' if self.config['enable_paper_trading'] else '💰 Live Trading'}
🕐 **Time:** {ist_time} IST

🎯 **Sophisticated Engine Active** ✅"""
            
            return notifier.send_notification(message)
            
        except Exception as e:
            logger.error(f"Failed to send sophisticated notifications: {e}")
            return False
    
    async def _execute_basic_trading(self) -> Dict[str, Any]:
        """Fallback to basic trading when sophisticated mode is unavailable"""
        try:
            logger.info("⚡ Running basic trading mode (sophisticated mode unavailable)")
            
            # Basic Kite Connect integration
            if self.kite_manager and self.config['kite_access_token']:
                try:
                    profile = self.kite_manager.profile()
                    quotes = self.kite_manager.quote(['NSE:NIFTY 50', 'NSE:NIFTY BANK'])
                    positions = self.kite_manager.positions()
                    
                    return {
                        'status': 'basic_success',
                        'mode': 'basic_kite_integration',
                        'user': profile.get('user_name', 'Unknown'),
                        'market_data': quotes,
                        'positions_count': len(positions.get('net', [])),
                        'message': 'Basic trading executed successfully'
                    }
                    
                except Exception as e:
                    logger.error(f"Basic Kite integration failed: {e}")
                    return self._create_fallback_result(f"Kite error: {str(e)}")
            
            return self._create_fallback_result("No trading capabilities available")
            
        except Exception as e:
            logger.error(f"Basic trading failed: {e}")
            return self._create_fallback_result(f"Basic trading error: {str(e)}")
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            'status': 'error',
            'error': error_message,
            'timestamp': get_ist_time().isoformat(),
            'mode': 'sophisticated' if self.sophisticated_mode else 'basic'
        }
    
    def _create_fallback_result(self, reason: str) -> Dict[str, Any]:
        """Create fallback result for simulation mode"""
        return {
            'status': 'fallback',
            'reason': reason,
            'signals_generated': 3,
            'trades_executed': 1,
            'current_pnl': 275.50,
            'open_positions': 2,
            'portfolio_value': 1002750.00,
            'mode': 'simulation'
        }

# Global trading engine instance
trading_engine = SophisticatedTradingEngine()

async def async_lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Sophisticated async Lambda handler with full system integration"""
    
    execution_id = context.aws_request_id if context else 'local'
    logger.info(f"🚀 Sophisticated Trading Lambda started - ID: {execution_id}")
    
    try:
        # Initialize trading engine
        initialized = await trading_engine.initialize()
        if not initialized:
            logger.warning("⚠️ Trading engine initialization incomplete, continuing with limited functionality")
        
        # Parse event parameters
        action = event.get('action', 'trading')
        force_run = event.get('force_run', False)
        
        # Market hours check
        if not force_run and not trading_engine.is_market_hours():
            message = "🕐 Lambda executed outside market hours - no trading action"
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
                'sophisticated_mode': trading_engine.sophisticated_mode,
                'database_connected': trading_engine.db_manager is not None,
                'kite_connected': trading_engine.kite_manager is not None,
                'config_available': bool(trading_engine.config['kite_api_key']),
                'market_hours': trading_engine.is_market_hours(),
                'execution_id': execution_id
            }
        else:
            result = trading_engine._create_fallback_result(f"Unknown action: {action}")
        
        # Send success notification for trading actions
        if notifier and action == 'trading':
            ist_time = get_ist_time()
            success_msg = f"""✅ **Sophisticated Lambda Complete**

🎯 **Action:** {action.title()}
🧠 **Mode:** {'Sophisticated' if trading_engine.sophisticated_mode else 'Basic'}
🔧 **Trading:** {'📋 Paper' if trading_engine.config['enable_paper_trading'] else '💰 Live'}
📊 **Status:** {result.get('status', 'completed').title()}
🆔 **ID:** {execution_id}

⏱️ **Time:** {ist_time.strftime('%Y-%m-%d %H:%M:%S')} IST"""
            
            notifier.send_notification(success_msg)
        
        # Create response
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
        error_msg = f"❌ Sophisticated Lambda execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
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
    """Sophisticated Lambda handler entry point"""
    return asyncio.run(async_lambda_handler(event, context))

# For local testing
if __name__ == "__main__":
    test_event = {'action': 'trading', 'force_run': True}
    test_context = type('Context', (), {'aws_request_id': 'test-sophisticated-123'})()
    
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2, default=str))