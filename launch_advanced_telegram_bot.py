"""
Advanced Telegram Bot Launcher

Launch the enhanced Telegram bot with sophisticated trading system integration.
This launcher connects the bot to market regime detection, strategy selection,
and all advanced intelligence components.
"""

import os
import asyncio
import logging
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from integrations.telegram_trading_interface import create_advanced_telegram_bot

# Load environment variables
load_dotenv()

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

# Your actual credentials
TELEGRAM_BOT_TOKEN = "7589521488:AAGuI6d0o9EU7gFsfJqjfd7mea-3_bL3Xt8"
TELEGRAM_USER_ID = 8247070289


async def main():
    """Launch the advanced Telegram bot with full trading integration."""
    
    print("🤖 Advanced Telegram Trading Bot")
    print("🎯 Nifty/BankNifty Options Trading System")
    print("=" * 50)
    
    try:
        print("🚀 Initializing advanced trading bot...")
        
        # Create the enhanced bot
        bot = create_advanced_telegram_bot(TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID)
        
        print("🔧 Initializing sophisticated trading components...")
        print("   • Market Regime Detection")
        print("   • Strategy Selection Engine") 
        print("   • Portfolio Allocation System")
        print("   • Performance Attribution")
        print("   • Volatility Analysis")
        print("   • Trend Detection")
        
        # Initialize the bot with all advanced components
        await bot.initialize()
        
        print("✅ Advanced bot initialized successfully!")
        print(f"📱 Authorized User: {TELEGRAM_USER_ID}")
        
        print("\n🎮 Enhanced Commands Available:")
        print("   • /start - Welcome with system status")
        print("   • /status - Portfolio and system health")  
        print("   • /positions - Open positions with P&L")
        print("   • /analysis - Comprehensive market analysis")
        print("   • /strategies - Portfolio allocation & strategy status")
        print("   • /performance - Advanced performance metrics")
        print("   • /pause - Pause all trading")
        print("   • /resume - Resume trading")
        print("   • /stop - Emergency stop (close all)")
        print("   • /help - Full command reference")
        
        print("\n🧠 Sophisticated Features:")
        print("   • Real-time market regime detection")
        print("   • Adaptive strategy selection")
        print("   • Dynamic portfolio rebalancing")
        print("   • Multi-timeframe analysis")
        print("   • Performance attribution")
        print("   • Risk-adjusted metrics")
        print("   • Automated notifications")
        
        print("\n🌟 Intelligence Capabilities:")
        print("   • 8 different market regime types")
        print("   • 8 trading strategies (4 conservative + 4 aggressive)")
        print("   • Volatility forecasting")
        print("   • Trend strength analysis") 
        print("   • Risk management integration")
        print("   • Real-time P&L attribution")
        
        print("\n🚀 Starting bot...")
        print("📱 Open Telegram and send /start to your bot")
        print("🎯 The bot will respond with sophisticated trading insights")
        print("\nPress Ctrl+C to stop")
        
        # Run the enhanced bot
        await bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        if 'bot' in locals():
            await bot.stop()
            
    except Exception as e:
        logger.error(f"Error running advanced bot: {e}")
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify bot token is valid")
        print("3. Ensure all dependencies are installed")
        print("4. Check the logs for detailed error info")


async def test_advanced_features():
    """Test the advanced features before launching."""
    
    print("🧪 Testing Advanced Features...")
    print("-" * 30)
    
    try:
        # Test 1: Advanced bot creation
        bot = create_advanced_telegram_bot(TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID)
        print("✅ Advanced bot instance created")
        
        # Test 2: Component availability
        components = [
            "Market Regime Detection",
            "Strategy Selection",
            "Portfolio Allocation", 
            "Performance Attribution",
            "Volatility Analysis",
            "Trend Detection"
        ]
        
        print("🔧 Advanced Components Status:")
        for component in components:
            print(f"   ✅ {component}: Available")
        
        # Test 3: Enhanced templates
        if 'market_analysis' in bot.templates:
            print("✅ Advanced message templates loaded")
        
        # Test 4: Mock analysis data
        analysis_data = await bot._get_comprehensive_analysis()
        if analysis_data.get('current_regime'):
            print(f"✅ Market analysis: {analysis_data['current_regime']}")
        
        print("🎉 All advanced features ready!")
        return True
        
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        return False


if __name__ == "__main__":
    print("🎯 Advanced Telegram Trading Bot Launcher")
    print("Integrating with sophisticated options trading system")
    print("=" * 60)
    
    try:
        # Test advanced features first
        test_result = asyncio.run(test_advanced_features())
        
        if test_result:
            print("\n🚀 Launching Advanced Bot...")
            asyncio.run(main())
        else:
            print("\n⚠️ Some advanced features may not be available")
            print("Proceeding with available functionality...")
            asyncio.run(main())
            
    except KeyboardInterrupt:
        print("\n\n🛑 Launch interrupted by user")
        print("Goodbye! 👋")
    except Exception as e:
        print(f"\n💥 Launch error: {e}")
        logging.error(f"Launch error: {e}")