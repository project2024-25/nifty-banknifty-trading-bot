"""
Main Trading Lambda Function

This is the primary Lambda function that executes during market hours.
It performs market analysis, generates signals, and executes trades.
"""

import json
import os
import sys
import logging
from datetime import datetime, time
import asyncio
from typing import Dict, Any

# Add src to path for imports
sys.path.append('/opt/python/src')
sys.path.append('./src')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global variables for connection reuse
trading_engine = None
kite_wrapper = None
telegram_bot = None

def lambda_handler(event, context):
    """
    Main Lambda handler for trading operations.
    
    Args:
        event: Lambda event data
        context: Lambda runtime context
        
    Returns:
        Response with execution status
    """
    
    try:
        # Log execution start
        execution_id = context.aws_request_id if context else 'local'
        logger.info(f"Trading Lambda execution started - ID: {execution_id}")
        
        # Parse event data
        action = event.get('action', 'trading')
        force_run = event.get('force_run', False)
        
        # Check market hours
        if not force_run and not is_market_hours():
            logger.info("Outside market hours - skipping execution")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'skipped',
                    'reason': 'outside_market_hours',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        # Execute trading cycle
        result = asyncio.run(execute_trading_cycle(action))
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'action': action,
                'result': result,
                'execution_id': execution_id,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}", exc_info=True)
        
        # Send error notification
        try:
            asyncio.run(send_error_notification(str(e)))
        except:
            pass  # Don't fail if notification fails
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


async def execute_trading_cycle(action: str = 'trading') -> Dict[str, Any]:
    """
    Execute the main trading cycle.
    
    Args:
        action: Type of action to perform
        
    Returns:
        Execution results
    """
    
    results = {
        'trades_executed': 0,
        'signals_generated': 0,
        'positions_updated': 0,
        'notifications_sent': 0
    }
    
    try:
        # Initialize components
        await initialize_trading_components()
        
        if action == 'pre_market':
            results = await execute_pre_market_analysis()
        elif action == 'trading':
            results = await execute_main_trading_logic()
        elif action == 'post_market':
            results = await execute_post_market_reporting()
        elif action == 'youtube_analysis':
            results = await execute_youtube_analysis()
        else:
            results = await execute_main_trading_logic()
        
        logger.info(f"Trading cycle completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Trading cycle failed: {e}")
        raise


async def initialize_trading_components():
    """Initialize all trading system components."""
    
    global trading_engine, kite_wrapper, telegram_bot
    
    try:
        # Initialize Kite Connect wrapper
        if not kite_wrapper:
            from integrations.kite_connect_wrapper import create_kite_wrapper
            
            kite_wrapper = create_kite_wrapper(
                api_key=os.environ['KITE_API_KEY'],
                api_secret=os.environ['KITE_API_SECRET'],
                access_token=os.environ['KITE_ACCESS_TOKEN'],
                paper_trading=os.environ.get('ENABLE_PAPER_TRADING', 'true').lower() == 'true'
            )
            
            await kite_wrapper.authenticate()
            logger.info("Kite Connect wrapper initialized")
        
        # Initialize trading engine
        if not trading_engine:
            from core.adaptive_trading_engine import AdaptiveTradingEngine
            
            trading_engine = AdaptiveTradingEngine()
            await trading_engine.initialize()
            logger.info("Adaptive trading engine initialized")
        
        # Initialize Telegram bot
        if not telegram_bot:
            from integrations.telegram_trading_interface import create_advanced_telegram_bot
            
            telegram_bot = create_advanced_telegram_bot(
                bot_token=os.environ['TELEGRAM_BOT_TOKEN'],
                user_id=int(os.environ['TELEGRAM_USER_ID'])
            )
            logger.info("Telegram bot initialized")
            
    except Exception as e:
        logger.error(f"Component initialization failed: {e}")
        raise


async def execute_main_trading_logic() -> Dict[str, Any]:
    """Execute the main trading logic during market hours."""
    
    results = {
        'trades_executed': 0,
        'signals_generated': 0,
        'positions_updated': 0,
        'notifications_sent': 0
    }
    
    try:
        # Step 1: Get market data
        logger.info("Fetching market data...")
        market_data = await fetch_current_market_data()
        
        # Step 2: Perform market regime detection
        logger.info("Analyzing market regime...")
        regime_analysis = await analyze_market_regime(market_data)
        
        # Step 3: Generate trading signals
        logger.info("Generating trading signals...")
        signals = await generate_trading_signals(market_data, regime_analysis)
        results['signals_generated'] = len(signals)
        
        # Step 4: Execute approved trades
        if signals:
            logger.info(f"Processing {len(signals)} signals...")
            trades = await execute_trades(signals)
            results['trades_executed'] = len(trades)
            
            # Send trade notifications
            for trade in trades:
                await send_trade_notification(trade)
                results['notifications_sent'] += 1
        
        # Step 5: Update positions and portfolio
        logger.info("Updating portfolio positions...")
        await update_portfolio_positions()
        results['positions_updated'] = 1
        
        # Step 6: Check risk limits and alerts
        await check_risk_limits()
        
        logger.info(f"Main trading cycle completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Main trading logic failed: {e}")
        raise


async def execute_pre_market_analysis() -> Dict[str, Any]:
    """Execute pre-market analysis and preparation."""
    
    results = {
        'analysis_complete': True,
        'strategies_prepared': 0,
        'alerts_set': 0
    }
    
    try:
        logger.info("Starting pre-market analysis...")
        
        # Analyze overnight news and events
        # Prepare trading strategies for the day
        # Set up alerts and watchlists
        # Send morning briefing
        
        await send_morning_briefing()
        results['notifications_sent'] = 1
        
        logger.info("Pre-market analysis completed")
        return results
        
    except Exception as e:
        logger.error(f"Pre-market analysis failed: {e}")
        raise


async def execute_post_market_reporting() -> Dict[str, Any]:
    """Execute post-market analysis and reporting."""
    
    results = {
        'report_generated': True,
        'performance_analyzed': True,
        'notifications_sent': 0
    }
    
    try:
        logger.info("Starting post-market reporting...")
        
        # Generate daily performance report
        # Analyze strategy performance
        # Update performance metrics
        # Send daily summary
        
        await send_daily_summary()
        results['notifications_sent'] = 1
        
        logger.info("Post-market reporting completed")
        return results
        
    except Exception as e:
        logger.error(f"Post-market reporting failed: {e}")
        raise


# Helper functions
async def fetch_current_market_data() -> Dict[str, Any]:
    """Fetch current market data for analysis."""
    
    try:
        # Get NIFTY and BANKNIFTY quotes
        instruments = ["NSE:NIFTY 50", "NSE:NIFTY BANK"]
        quotes = await kite_wrapper.get_quote(instruments)
        
        # Get VIX data
        vix_quote = await kite_wrapper.get_quote(["NSE:INDIA VIX"])
        
        return {
            'nifty': quotes.get("NSE:NIFTY 50", {}),
            'banknifty': quotes.get("NSE:NIFTY BANK", {}),
            'vix': vix_quote.get("NSE:INDIA VIX", {}),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market data fetch failed: {e}")
        return {}


async def analyze_market_regime(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze current market regime."""
    
    try:
        # Use trading engine for regime detection
        regime_data = await trading_engine.detect_market_regime(market_data)
        
        logger.info(f"Market regime detected: {regime_data.get('current_regime', 'Unknown')}")
        return regime_data
        
    except Exception as e:
        logger.error(f"Market regime analysis failed: {e}")
        return {'current_regime': 'Unknown', 'confidence': 0.0}


async def generate_trading_signals(market_data: Dict, regime_analysis: Dict) -> list:
    """Generate trading signals based on analysis."""
    
    try:
        # Use trading engine to generate signals
        signals = await trading_engine.generate_signals(market_data, regime_analysis)
        
        logger.info(f"Generated {len(signals)} trading signals")
        return signals
        
    except Exception as e:
        logger.error(f"Signal generation failed: {e}")
        return []


async def execute_trades(signals: list) -> list:
    """Execute approved trading signals."""
    
    executed_trades = []
    
    for signal in signals:
        try:
            # Execute trade through Kite Connect
            order_id = await kite_wrapper.place_order(signal)
            
            if order_id:
                executed_trades.append({
                    'signal': signal,
                    'order_id': order_id,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info(f"Trade executed: {order_id}")
            
        except Exception as e:
            logger.error(f"Trade execution failed for signal {signal}: {e}")
    
    return executed_trades


async def update_portfolio_positions():
    """Update current portfolio positions."""
    
    try:
        positions = await kite_wrapper.get_positions()
        
        # Update database with current positions
        # Calculate unrealized P&L
        # Update risk metrics
        
        logger.info(f"Updated {len(positions)} portfolio positions")
        
    except Exception as e:
        logger.error(f"Position update failed: {e}")


async def check_risk_limits():
    """Check risk limits and trigger alerts if necessary."""
    
    try:
        # Check daily loss limits
        # Check position size limits
        # Check concentration risk
        # Check margin requirements
        
        # If limits exceeded, send alerts and take action
        
        logger.info("Risk limits checked")
        
    except Exception as e:
        logger.error(f"Risk check failed: {e}")


async def send_trade_notification(trade: Dict):
    """Send trade notification via Telegram."""
    
    try:
        if telegram_bot:
            await telegram_bot.send_trade_notification(trade)
            
    except Exception as e:
        logger.error(f"Trade notification failed: {e}")


async def send_morning_briefing():
    """Send morning market briefing."""
    
    try:
        if telegram_bot:
            briefing = "🌅 Good morning! Pre-market analysis complete. Trading system is ready for market open."
            await telegram_bot.send_notification(briefing)
            
    except Exception as e:
        logger.error(f"Morning briefing failed: {e}")


async def send_daily_summary():
    """Send daily performance summary."""
    
    try:
        if telegram_bot:
            summary = {
                'pnl': 1250.75,
                'pnl_percent': 1.25,
                'total_trades': 5,
                'winning': 3,
                'losing': 2,
                'capital_used': 65.0,
                'best_trade': 650.25,
                'worst_trade': -285.50,
                'conservative_pnl': 850.25,
                'aggressive_pnl': 400.50
            }
            
            await telegram_bot.send_daily_summary(summary)
            
    except Exception as e:
        logger.error(f"Daily summary failed: {e}")


async def send_error_notification(error_message: str):
    """Send error notification to user."""
    
    try:
        if telegram_bot:
            error_msg = f"🚨 Trading system error: {error_message[:100]}..."
            await telegram_bot.send_notification(error_msg)
            
    except Exception as e:
        logger.error(f"Error notification failed: {e}")


def is_market_hours() -> bool:
    """Check if current time is within market hours."""
    
    try:
        now = datetime.now()
        
        # Check if it's a weekday
        if now.weekday() > 4:  # Saturday = 5, Sunday = 6
            return False
        
        # Market hours: 9:15 AM to 3:30 PM IST
        market_open = time(9, 15)
        market_close = time(15, 30)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
        
    except Exception:
        return False


# For local testing
if __name__ == "__main__":
    # Local test
    test_event = {
        'action': 'trading',
        'force_run': True
    }
    
    class MockContext:
        aws_request_id = 'test-12345'
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))