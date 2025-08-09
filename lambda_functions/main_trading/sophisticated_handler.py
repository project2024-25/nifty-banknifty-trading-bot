"""
Full Sophisticated Lambda Handler
Complete trading system with market intelligence, strategy selection, and database integration
"""

import json
import os
import sys
import logging
import traceback
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

# Import sophisticated components with COMPREHENSIVE DIAGNOSTICS
logger.info("🔍 LAMBDA DIAGNOSTIC: Starting sophisticated component imports...")

# Log Lambda environment info
logger.info(f"🔍 Python version: {sys.version}")
logger.info(f"🔍 Python path: {sys.path[:3]}...")  # First 3 entries
logger.info(f"🔍 Current working directory: {os.getcwd()}")
logger.info(f"🔍 __file__ location: {__file__}")

# Test package availability
logger.info("🔍 PACKAGE AVAILABILITY TEST:")
test_packages = ['supabase', 'kiteconnect', 'pandas', 'numpy', 'scipy', 'sklearn']
for package in test_packages:
    try:
        __import__(package)
        logger.info(f"✅ {package}: Available")
    except ImportError as e:
        logger.error(f"❌ {package}: Missing - {e}")

try:
    # Add source paths for sophisticated components with diagnostics
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    logger.info(f"🔍 Calculated source directory: {current_dir}")
    
    # Check if source directory exists
    src_dir = os.path.join(current_dir, 'src')
    logger.info(f"🔍 Source directory exists: {os.path.exists(src_dir)}")
    if os.path.exists(src_dir):
        logger.info(f"🔍 Source directory contents: {os.listdir(src_dir)[:5]}")  # First 5 items
    
    sys.path.insert(0, current_dir)
    logger.info(f"🔍 Added to Python path: {current_dir}")
    
    # Try importing each module individually with detailed error reporting
    import_results = {}
    
    modules_to_import = [
        ('DatabaseManager', 'src.integrations.database', 'DatabaseManager'),
        ('MarketRegimeDetector', 'src.intelligence.market_regime', 'MarketRegimeDetector'),
        ('AdaptiveStrategySelector', 'src.intelligence.strategy_selector', 'AdaptiveStrategySelector'),
        ('DynamicAllocationManager', 'src.intelligence.dynamic_allocator', 'DynamicAllocationManager'),
        ('AllocationMode', 'src.intelligence.dynamic_allocator', 'AllocationMode'),
        ('SimpleMarketDashboard', 'src.intelligence.dashboard_simple', 'SimpleMarketDashboard'),
        ('MultiTimeframeAnalyzer', 'src.intelligence.multi_timeframe', 'MultiTimeframeAnalyzer'),
        ('create_kite_wrapper', 'src.integrations.kite_connect_wrapper', 'create_kite_wrapper')
    ]
    
    successful_imports = {}
    
    for name, module_path, class_name in modules_to_import:
        try:
            logger.info(f"🔍 Attempting to import {name} from {module_path}")
            
            # Try the import
            module = __import__(module_path, fromlist=[class_name])
            class_obj = getattr(module, class_name)
            successful_imports[name] = class_obj
            
            logger.info(f"✅ Successfully imported {name}")
            import_results[name] = "SUCCESS"
            
        except ImportError as e:
            logger.error(f"❌ Failed to import {name}: {e}")
            import_results[name] = f"IMPORT_ERROR: {e}"
        except AttributeError as e:
            logger.error(f"❌ Failed to get {class_name} from {module_path}: {e}")
            import_results[name] = f"ATTRIBUTE_ERROR: {e}"
        except Exception as e:
            logger.error(f"❌ Unexpected error importing {name}: {e}")
            import_results[name] = f"UNEXPECTED_ERROR: {e}"
    
    # Log import summary
    successful_count = len([r for r in import_results.values() if r == "SUCCESS"])
    total_count = len(import_results)
    
    logger.info(f"🔍 Import summary: {successful_count}/{total_count} successful")
    for name, result in import_results.items():
        logger.info(f"   {name}: {result}")
    
    # Set up imports if we got enough successful imports
    if successful_count >= 6:  # Need at least 6 core components
        # Assign the successful imports
        DatabaseManager = successful_imports.get('DatabaseManager')
        MarketRegimeDetector = successful_imports.get('MarketRegimeDetector')
        AdaptiveStrategySelector = successful_imports.get('AdaptiveStrategySelector')
        DynamicAllocationManager = successful_imports.get('DynamicAllocationManager')
        AllocationMode = successful_imports.get('AllocationMode')
        SimpleMarketDashboard = successful_imports.get('SimpleMarketDashboard')
        MultiTimeframeAnalyzer = successful_imports.get('MultiTimeframeAnalyzer')
        create_kite_wrapper = successful_imports.get('create_kite_wrapper')
        
        SOPHISTICATED_MODE = True
        logger.info(f"✅ SOPHISTICATED MODE ENABLED with {successful_count}/{total_count} components")
    else:
        SOPHISTICATED_MODE = False
        logger.warning(f"⚠️ SOPHISTICATED MODE DISABLED - only {successful_count}/{total_count} components available")
    
except Exception as import_error:
    logger.error(f"❌ Critical error in sophisticated import process: {import_error}")
    logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    SOPHISTICATED_MODE = False

# Enhanced fallback simplified components for when sophisticated imports fail
if not SOPHISTICATED_MODE:
    class DatabaseManager:
        def __init__(self): 
            self.client = None
            self.connection = None
            self.supabase_url = os.getenv('SUPABASE_URL', '')
            self.supabase_key = os.getenv('SUPABASE_KEY', '')
        
        async def initialize(self):
            logger.info("🔄 DatabaseManager fallback initialization starting...")
            logger.info(f"   Supabase URL present: {bool(self.supabase_url)}")
            logger.info(f"   Supabase Key present: {bool(self.supabase_key)}")
            
            try:
                # Try Supabase client first
                try:
                    from supabase import create_client
                    if self.supabase_url and self.supabase_key:
                        logger.info("🔄 Creating Supabase client...")
                        self.client = create_client(self.supabase_url, self.supabase_key)
                        
                        # Test the connection with a simple query
                        try:
                            # Try to access system_logs table as a connection test
                            test_result = self.client.table('system_logs').select('id').limit(1).execute()
                            logger.info("✅ Supabase client initialized and tested successfully")
                            return True
                        except Exception as test_error:
                            logger.error(f"❌ Supabase connection test failed: {test_error}")
                            return False
                            
                    else:
                        logger.error("❌ Missing Supabase URL or Key")
                        return False
                        
                except ImportError as import_error:
                    logger.error(f"❌ Supabase package not available: {import_error}")
                    logger.info("🔄 Attempting direct PostgreSQL fallback...")
                
                # Fallback to direct PostgreSQL connection
                try:
                    import psycopg2
                    if self.supabase_url and 'supabase.co' in self.supabase_url:
                        logger.info("✅ PostgreSQL driver available (direct connection would need full credentials)")
                        # Note: Direct PostgreSQL would need host, port, db, user, password
                        # For now, we'll return False as we don't have those details
                        return False
                except ImportError:
                    logger.error("❌ Neither supabase nor psycopg2 packages available")
                        
            except Exception as e:
                logger.error(f"❌ Database initialization failed with exception: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
        
        async def create_trade(self, trade_data):
            if self.client:
                try:
                    result = self.client.table('trades').insert(trade_data).execute()
                    return result.data[0]['id'] if result.data else None
                except Exception as e:
                    logger.error(f"Failed to create trade: {e}")
            else:
                # Fallback: Log trade data for now (can be enhanced with direct SQL later)
                logger.info(f"Trade logged: {trade_data.get('symbol', 'Unknown')} - {trade_data.get('strategy', 'Unknown')}")
            return None
        
        async def create_signal(self, signal_data):
            if self.client:
                try:
                    result = self.client.table('signals').insert(signal_data).execute()
                    return result.data[0]['id'] if result.data else None
                except Exception as e:
                    logger.error(f"Failed to create signal: {e}")
            else:
                # Fallback: Log signal data
                logger.info(f"Signal logged: {signal_data.get('symbol', 'Unknown')} - {signal_data.get('signal_type', 'Unknown')}")
            return None
        
        async def store_intelligence(self, intelligence_data):
            if self.client:
                try:
                    result = self.client.table('market_intelligence').insert(intelligence_data).execute()
                    return result.data[0]['id'] if result.data else None
                except Exception as e:
                    logger.error(f"Failed to store intelligence: {e}")
            else:
                # Fallback: Log intelligence data  
                logger.info(f"Intelligence logged: {intelligence_data.get('title', 'Market Analysis')}")
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
    """Full sophisticated trading engine with all features including Kite Connect and multi-timeframe analysis"""
    
    def __init__(self):
        self.config = self._get_config()
        self.db_manager = None
        self.kite_manager = None
        self.kite_wrapper = None
        self.multi_timeframe_analyzer = None
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
        """Get configuration from environment variables with enhanced debugging."""
        
        # COMPREHENSIVE environment variable diagnostics
        logger.info("🔍 ENVIRONMENT VARIABLE DIAGNOSTIC:")
        
        # Check all environment variables
        all_env_vars = dict(os.environ)
        trading_vars = {k: v for k, v in all_env_vars.items() if any(keyword in k.upper() for keyword in 
                       ['KITE', 'SUPABASE', 'TELEGRAM', 'TRADING', 'PAPER'])}
        
        logger.info(f"🔍 Total environment variables: {len(all_env_vars)}")
        logger.info(f"🔍 Trading-related variables found: {len(trading_vars)}")
        
        for var_name in trading_vars:
            # Log existence without exposing values
            value = trading_vars[var_name]
            logger.info(f"🔍   {var_name}: {'✅ Set' if value else '❌ Empty'} ({len(value)} chars)")
        
        # Enhanced environment variable debugging for Lambda
        kite_api_key = os.getenv('KITE_API_KEY', '')
        kite_api_secret = os.getenv('KITE_API_SECRET', '')
        kite_access_token = os.getenv('KITE_ACCESS_TOKEN', '')
        supabase_url = os.getenv('SUPABASE_URL', '')
        supabase_key = os.getenv('SUPABASE_KEY', '')
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        
        # Log configuration status (without exposing sensitive data)
        logger.info(f"🔧 CONFIGURATION LOADED:")
        logger.info(f"   Kite API Key: {'✅ Available' if kite_api_key else '❌ Missing'} ({len(kite_api_key)} chars)")
        logger.info(f"   Kite API Secret: {'✅ Available' if kite_api_secret else '❌ Missing'} ({len(kite_api_secret)} chars)")
        logger.info(f"   Kite Access Token: {'✅ Available' if kite_access_token else '❌ Missing'} ({len(kite_access_token)} chars)")
        logger.info(f"   Supabase URL: {'✅ Available' if supabase_url else '❌ Missing'} ({'supabase.co' in supabase_url if supabase_url else 'N/A'})")
        logger.info(f"   Supabase Key: {'✅ Available' if supabase_key else '❌ Missing'} ({len(supabase_key)} chars)")
        logger.info(f"   Telegram Token: {'✅ Available' if telegram_token else '❌ Missing'} ({len(telegram_token)} chars)")
        logger.info(f"   Paper Trading: {os.getenv('ENABLE_PAPER_TRADING', 'true')}")
        
        return {
            'kite_api_key': kite_api_key,
            'kite_api_secret': os.getenv('KITE_API_SECRET', ''),
            'kite_access_token': os.getenv('KITE_ACCESS_TOKEN', ''),
            'supabase_url': supabase_url,
            'supabase_key': supabase_key,
            'enable_paper_trading': os.getenv('ENABLE_PAPER_TRADING', 'true').lower() == 'true',
            'trading_capital': float(os.getenv('TRADING_CAPITAL', '100000')),
            'telegram_user_id': int(os.getenv('TELEGRAM_USER_ID', '0')),
            'max_daily_loss_percent': float(os.getenv('MAX_DAILY_LOSS_PERCENT', '3'))
        }
    
    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Initialize database with enhanced debugging
            if self.db_manager and self.config['supabase_url']:
                logger.info(f"🔄 Attempting database initialization...")
                logger.info(f"   URL configured: {bool(self.config['supabase_url'])}")
                logger.info(f"   Key configured: {bool(self.config['supabase_key'])}")
                
                try:
                    db_success = await self.db_manager.initialize()
                    if db_success:
                        logger.info("✅ Database connection established successfully")
                    else:
                        logger.error("❌ Database connection failed - initialize returned False")
                except Exception as db_error:
                    logger.error(f"❌ Database initialization exception: {db_error}")
                    db_success = False
            else:
                logger.warning("⚠️ Database initialization skipped - missing URL or manager")
                db_success = False
            
            # Initialize Kite Connect wrapper (sophisticated version)
            if self.config['kite_api_key'] and SOPHISTICATED_MODE:
                try:
                    self.kite_wrapper = create_kite_wrapper(
                        api_key=self.config['kite_api_key'],
                        api_secret=self.config.get('kite_api_secret', ''),
                        access_token=self.config.get('kite_access_token'),
                        paper_trading=self.config.get('enable_paper_trading', True)
                    )
                    
                    # Initialize the wrapper
                    kite_success = await self.kite_wrapper.authenticate()
                    if kite_success:
                        logger.info("✅ Sophisticated Kite Connect wrapper initialized successfully")
                    else:
                        logger.warning("⚠️ Kite Connect authentication failed, using paper trading mode")
                    
                    # Initialize multi-timeframe analyzer with Kite wrapper
                    self.multi_timeframe_analyzer = MultiTimeframeAnalyzer(kite_wrapper=self.kite_wrapper)
                    logger.info("✅ Multi-timeframe analyzer initialized")
                    
                except Exception as e:
                    logger.error(f"❌ Sophisticated Kite Connect initialization failed: {e}")
                    self.kite_wrapper = None
                    
                    # Initialize multi-timeframe analyzer without Kite (fallback mode)
                    try:
                        self.multi_timeframe_analyzer = MultiTimeframeAnalyzer()
                        logger.info("✅ Multi-timeframe analyzer initialized in fallback mode")
                    except Exception as analyzer_error:
                        logger.error(f"❌ Multi-timeframe analyzer initialization failed: {analyzer_error}")
                        self.multi_timeframe_analyzer = None
            
            # Fallback Kite Connect (original simple version)
            elif self.config['kite_api_key']:
                try:
                    import kiteconnect
                    from kiteconnect import KiteConnect
                    
                    self.kite_manager = KiteConnect(api_key=self.config['kite_api_key'])
                    if self.config['kite_access_token']:
                        self.kite_manager.set_access_token(self.config['kite_access_token'])
                    
                    # Test connection
                    profile = self.kite_manager.profile()
                    logger.info(f"✅ Basic Kite Connect initialized for user: {profile.get('user_name', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"❌ Basic Kite Connect initialization failed: {e}")
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
        """Fetch comprehensive market data with multi-timeframe analysis"""
        try:
            market_data = {}
            
            # Basic market quotes
            if self.kite_wrapper:
                # Use sophisticated Kite wrapper
                instruments = ['NIFTY', 'BANKNIFTY']
                quotes = await self.kite_wrapper.get_quote(instruments)
                positions = await self.kite_wrapper.get_positions()
                
                market_data = {
                    'quotes': quotes,
                    'positions': positions,
                    'timestamp': get_ist_time().isoformat(),
                    'data_source': 'sophisticated_kite'
                }
                
            elif self.kite_manager and self.config.get('kite_access_token'):
                # Use basic Kite manager
                instruments = ['NSE:NIFTY 50', 'NSE:NIFTY BANK', 'NSE:NIFTY FIN SERVICE']
                quotes = self.kite_manager.quote(instruments)
                positions = self.kite_manager.positions()
                
                market_data = {
                    'quotes': quotes,
                    'positions': positions,
                    'timestamp': get_ist_time().isoformat(),
                    'data_source': 'basic_kite'
                }
                
            else:
                # Fallback to mock data
                logger.warning("No Kite connection available, using mock data")
                market_data = {
                    'quotes': {
                        'NIFTY': {'last_price': 25000, 'net_change': 125, 'buy_price': 24995, 'sell_price': 25005},
                        'BANKNIFTY': {'last_price': 52000, 'net_change': 250, 'buy_price': 51990, 'sell_price': 52010}
                    },
                    'positions': [],
                    'timestamp': get_ist_time().isoformat(),
                    'data_source': 'mock'
                }
            
            # Add multi-timeframe analysis if available
            if self.multi_timeframe_analyzer:
                try:
                    logger.info("🔍 Performing multi-timeframe analysis...")
                    
                    # Analyze NIFTY
                    nifty_analysis = await self.multi_timeframe_analyzer.analyze_symbol(
                        'NIFTY', 
                        use_real_data=(self.kite_wrapper is not None)
                    )
                    
                    # Analyze BANKNIFTY
                    banknifty_analysis = await self.multi_timeframe_analyzer.analyze_symbol(
                        'BANKNIFTY',
                        use_real_data=(self.kite_wrapper is not None)
                    )
                    
                    # Add multi-timeframe data
                    market_data['multi_timeframe'] = {
                        'nifty': {
                            'overall_trend': nifty_analysis.overall_trend,
                            'confidence': nifty_analysis.overall_confidence,
                            'market_regime': nifty_analysis.market_regime,
                            'entry_zones': nifty_analysis.entry_zones,
                            'risk_levels': nifty_analysis.risk_levels,
                            'recommendations': nifty_analysis.recommendations,
                            'timeframes': {tf: {'trend': signal.trend, 'strength': signal.strength, 'confidence': signal.confidence} 
                                         for tf, signal in nifty_analysis.timeframes.items()}
                        },
                        'banknifty': {
                            'overall_trend': banknifty_analysis.overall_trend,
                            'confidence': banknifty_analysis.overall_confidence,
                            'market_regime': banknifty_analysis.market_regime,
                            'entry_zones': banknifty_analysis.entry_zones,
                            'risk_levels': banknifty_analysis.risk_levels,
                            'recommendations': banknifty_analysis.recommendations,
                            'timeframes': {tf: {'trend': signal.trend, 'strength': signal.strength, 'confidence': signal.confidence}
                                         for tf, signal in banknifty_analysis.timeframes.items()}
                        },
                        'analysis_timestamp': get_ist_time().isoformat()
                    }
                    
                    logger.info(f"✅ Multi-timeframe analysis completed - NIFTY: {nifty_analysis.overall_trend} "
                               f"({nifty_analysis.overall_confidence:.1%}), BANKNIFTY: {banknifty_analysis.overall_trend} "
                               f"({banknifty_analysis.overall_confidence:.1%})")
                    
                except Exception as analysis_error:
                    logger.error(f"❌ Multi-timeframe analysis failed: {analysis_error}")
                    market_data['multi_timeframe'] = {'error': str(analysis_error)}
            
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to fetch comprehensive market data: {e}")
            return None
    
    async def _send_full_sophisticated_notifications(self, regime_analysis, strategy_recommendations, market_data, signals_generated, trades_executed):
        """Send comprehensive sophisticated notifications with multi-timeframe analysis"""
        try:
            if not notifier:
                return False
            
            # Extract market data (handle both old and new format)
            quotes = market_data.get('quotes', {})
            nifty_data = quotes.get('NIFTY', quotes.get('NSE:NIFTY 50', {}))
            bank_nifty_data = quotes.get('BANKNIFTY', quotes.get('NSE:NIFTY BANK', {}))
            
            # Get multi-timeframe analysis data
            multi_tf_data = market_data.get('multi_timeframe', {})
            nifty_mtf = multi_tf_data.get('nifty', {})
            banknifty_mtf = multi_tf_data.get('banknifty', {})
            
            # Get top strategy recommendation
            top_strategy = max(strategy_recommendations.items(), key=lambda x: x[1].get('confidence', 0)) if strategy_recommendations else ('None', {})
            
            # Build comprehensive message
            message = f"""🧠 **FULL SOPHISTICATED TRADING SYSTEM**

📊 **Market Intelligence:**
• Regime: {regime_analysis.get('regime', 'Unknown')} ({regime_analysis.get('confidence', 0):.1%} confidence)
• Volatility: {regime_analysis.get('volatility_regime', 'Unknown')}
• Trend Strength: {regime_analysis.get('trend_strength', 0):.2f}

📈 **Real-time Market Data:**
• Nifty: ₹{nifty_data.get('last_price', 'N/A')} ({nifty_data.get('net_change', 0):+.1f})
• Bank Nifty: ₹{bank_nifty_data.get('last_price', 'N/A')} ({bank_nifty_data.get('net_change', 0):+.1f})
• Data Source: {market_data.get('data_source', 'Unknown').title()}

🔍 **Multi-Timeframe Analysis:**"""
            
            # Add NIFTY multi-timeframe analysis
            if nifty_mtf:
                message += f"""
📊 NIFTY: {nifty_mtf.get('overall_trend', '').upper()} ({nifty_mtf.get('confidence', 0):.1%})
• Market Regime: {nifty_mtf.get('market_regime', 'Unknown')}
• Entry Zones: {len(nifty_mtf.get('entry_zones', []))} identified
• Risk Level: {nifty_mtf.get('risk_levels', {}).get('stop_loss', 0):.1%} SL"""
            
            # Add BANKNIFTY multi-timeframe analysis
            if banknifty_mtf:
                message += f"""
🏦 BANKNIFTY: {banknifty_mtf.get('overall_trend', '').upper()} ({banknifty_mtf.get('confidence', 0):.1%})
• Market Regime: {banknifty_mtf.get('market_regime', 'Unknown')}
• Entry Zones: {len(banknifty_mtf.get('entry_zones', []))} identified
• Risk Level: {banknifty_mtf.get('risk_levels', {}).get('stop_loss', 0):.1%} SL"""
            
            # Add timeframe breakdown if available
            if nifty_mtf.get('timeframes'):
                timeframes = nifty_mtf['timeframes']
                message += f"""
⏰ Timeframe Alignment (NIFTY):
• 5min: {timeframes.get('5min', {}).get('trend', 'N/A')} ({timeframes.get('5min', {}).get('confidence', 0):.1%})
• 15min: {timeframes.get('15min', {}).get('trend', 'N/A')} ({timeframes.get('15min', {}).get('confidence', 0):.1%})
• 1hour: {timeframes.get('1hour', {}).get('trend', 'N/A')} ({timeframes.get('1hour', {}).get('confidence', 0):.1%})
• Daily: {timeframes.get('daily', {}).get('trend', 'N/A')} ({timeframes.get('daily', {}).get('confidence', 0):.1%})"""
            
            message += f"""

💡 **Strategy Engine:**
• Top Strategy: {top_strategy[0]}
• Strategy Confidence: {top_strategy[1].get('confidence', 0):.1%}
• Rationale: {top_strategy[1].get('rationale', 'N/A')}

⚡ **Execution Summary:**
• Strategies Analyzed: {len(strategy_recommendations)}
• Signals Generated: {signals_generated}
• Trades Executed: {trades_executed}
• Mode: {'📋 Paper Trading' if self.config['enable_paper_trading'] else '💰 Live Trading'}

🎯 **System Status:**
• Engine: {'FULL SOPHISTICATED' if self.sophisticated_mode else 'FALLBACK SOPHISTICATED'}
• Database: {'✅ Connected' if self.db_manager and self.db_manager.client else '❌ Disconnected'}
• Kite Connect: {'✅ Sophisticated' if self.kite_wrapper else '✅ Basic' if self.kite_manager else '❌ Disconnected'}
• Multi-TF: {'✅ Active' if self.multi_timeframe_analyzer else '❌ Unavailable'}

🕐 **Time:** {format_ist_time()} IST

🚀 **Your Enterprise Trading System with Multi-Timeframe Intelligence is Active!**"""
            
            return notifier.send_notification(message)
            
        except Exception as e:
            logger.error(f"Failed to send sophisticated notifications: {e}")
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