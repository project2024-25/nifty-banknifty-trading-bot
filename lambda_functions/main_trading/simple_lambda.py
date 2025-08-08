"""
Simplified Trading Lambda Function
Uses minimal dependencies for reliable deployment
"""

import json
import os
import sys
import logging
from datetime import datetime, time, timezone
import pytz
from typing import Dict, Any

# Add lambda functions to path
sys.path.append('/opt/python')
sys.path.append('.')

# Import our simple telegram helper
try:
    from telegram_helper import send_notification, send_trade_notification, send_daily_summary
except ImportError:
    # Fallback functions if import fails
    def send_notification(msg):
        logging.info(f"Telegram notification: {msg}")
        return True
    def send_trade_notification(data):
        logging.info(f"Trade notification: {data}")
        return True
    def send_daily_summary(data):
        logging.info(f"Daily summary: {data}")
        return True

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def is_market_hours() -> bool:
    """Check if current time is within market hours (9:15 AM - 3:30 PM IST)."""
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Skip weekends
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Market hours: 9:15 AM to 3:30 PM IST
        market_open = time(9, 15)
        market_close = time(15, 30)
        current_time = now.time()
        
        return market_open <= current_time <= market_close
        
    except Exception as e:
        logger.error(f"Error checking market hours: {e}")
        return False

def lambda_handler(event, context):
    """
    Simplified Lambda handler for trading operations.
    
    Args:
        event: Lambda event data
        context: Lambda runtime context
        
    Returns:
        Response with execution status
    """
    
    try:
        # Log execution start
        execution_id = context.aws_request_id if context else 'local'
        logger.info(f"🚀 Trading Lambda execution started - ID: {execution_id}")
        
        # Parse event data
        action = event.get('action', 'trading')
        force_run = event.get('force_run', False)
        paper_trading = os.getenv('ENABLE_PAPER_TRADING', 'true').lower() == 'true'
        
        # Check market hours
        if not force_run and not is_market_hours():
            message = "🕐 Lambda executed outside market hours - no action taken"
            logger.info(message)
            send_notification(f"⏰ **Trading Bot Status**\n\n{message}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'skipped',
                    'reason': 'outside_market_hours',
                    'timestamp': datetime.now().isoformat(),
                    'execution_id': execution_id
                })
            }
        
        # Simulate trading logic for now
        if action == 'trading':
            result = simulate_trading_cycle(paper_trading)
        elif action == 'analysis':
            result = simulate_market_analysis()
        elif action == 'reporting':
            result = simulate_daily_reporting()
        else:
            raise ValueError(f"Unknown action: {action}")
        
        # Send success notification
        success_msg = f"""✅ **Lambda Execution Successful**

🔹 **Action:** {action.title()}
🔹 **Mode:** {'📋 Paper Trading' if paper_trading else '💰 Live Trading'}
🔹 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔹 **Execution ID:** {execution_id}

📊 **Result:** {result.get('message', 'Completed successfully')}"""
        
        send_notification(success_msg)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'action': action,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'execution_id': execution_id
            })
        }
        
    except Exception as e:
        error_msg = f"❌ Lambda execution failed: {str(e)}"
        logger.error(error_msg)
        send_notification(f"🚨 **Trading Bot Error**\n\n{error_msg}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'execution_id': execution_id if 'execution_id' in locals() else 'unknown'
            })
        }

def simulate_trading_cycle(paper_trading: bool) -> Dict[str, Any]:
    """Simulate a trading cycle - replace with actual trading logic later."""
    
    logger.info("🔄 Starting trading cycle simulation...")
    
    # Simulate market analysis
    market_analysis = {
        'trend': 'bullish',
        'volatility': 'medium',
        'regime': 'trending_up'
    }
    
    # Simulate trade execution
    if paper_trading:
        trade_result = {
            'symbol': 'NIFTY25FEB26000CE',
            'action': 'BUY',
            'quantity': 25,
            'price': 150.50,
            'strategy': 'Long Call',
            'pnl_impact': 0,  # Paper trading
            'portfolio_value': 100000
        }
        
        send_trade_notification(trade_result)
        
        return {
            'message': 'Paper trading cycle completed',
            'trades_executed': 1,
            'analysis': market_analysis,
            'mode': 'paper'
        }
    else:
        # Live trading logic would go here
        return {
            'message': 'Live trading not implemented yet',
            'trades_executed': 0,
            'analysis': market_analysis,
            'mode': 'live'
        }

def simulate_market_analysis() -> Dict[str, Any]:
    """Simulate market analysis - replace with actual analysis later."""
    
    logger.info("📊 Starting market analysis simulation...")
    
    analysis_result = {
        'timestamp': datetime.now().isoformat(),
        'indices': {
            'nifty': {'price': 24500, 'change': '+0.8%'},
            'banknifty': {'price': 52000, 'change': '+1.2%'}
        },
        'volatility': 'medium',
        'trend': 'bullish',
        'recommendations': ['Long Call strategies recommended', 'High probability setups available']
    }
    
    notification = f"""📈 **Market Analysis Complete**

📊 **Index Levels:**
• Nifty: {analysis_result['indices']['nifty']['price']} ({analysis_result['indices']['nifty']['change']})
• Bank Nifty: {analysis_result['indices']['banknifty']['price']} ({analysis_result['indices']['banknifty']['change']})

📋 **Assessment:**
• Trend: {analysis_result['trend'].title()}
• Volatility: {analysis_result['volatility'].title()}

💡 **Recommendations:**
{chr(10).join(f'• {rec}' for rec in analysis_result['recommendations'])}"""
    
    send_notification(notification)
    
    return analysis_result

def simulate_daily_reporting() -> Dict[str, Any]:
    """Simulate daily reporting - replace with actual reporting later."""
    
    logger.info("📋 Starting daily reporting simulation...")
    
    summary_data = {
        'daily_pnl': '+2,500',
        'total_trades': 5,
        'win_rate': '80',
        'portfolio_value': '1,02,500',
        'available_margin': '87,500',
        'open_positions': 2,
        'strategy_performance': 'Long Call: +₹1,500\nIron Condor: +₹1,000'
    }
    
    send_daily_summary(summary_data)
    
    return {
        'message': 'Daily report generated',
        'report_data': summary_data
    }

# For local testing
if __name__ == "__main__":
    # Test the function locally
    test_event = {'action': 'trading', 'force_run': True}
    test_context = type('Context', (), {'aws_request_id': 'test-123'})()
    
    result = lambda_handler(test_event, test_context)
    print(json.dumps(result, indent=2))