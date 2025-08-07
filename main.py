"""
Main entry point for the trading bot
"""
import asyncio
import argparse
from datetime import datetime

from src.utils.logger import get_logger
from src.utils.config import get_config, validate_config
from src.core.trading_engine import TradingEngine

logger = get_logger(__name__)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Nifty/BankNifty Trading Bot')
    parser.add_argument('--paper-trading', action='store_true', 
                       help='Run in paper trading mode')
    parser.add_argument('--validate-config', action='store_true',
                       help='Validate configuration and exit')
    
    args = parser.parse_args()
    
    logger.info("Starting Nifty/BankNifty Trading Bot", 
                version="0.1.0", 
                timestamp=datetime.now(),
                paper_trading=args.paper_trading)
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed. Please check your .env file")
        return 1
    
    if args.validate_config:
        logger.info("Configuration validation successful")
        return 0
    
    try:
        # Initialize trading engine
        engine = TradingEngine()
        engine.paper_trading = args.paper_trading or get_config().enable_paper_trading
        
        await engine.initialize()
        
        if args.paper_trading:
            logger.info("Running in PAPER TRADING mode - no real trades will be executed")
        
        # Run trading engine
        logger.info("Trading bot started successfully")
        
        # For now, just run one cycle for testing
        result = await engine.execute_trading_cycle()
        logger.info("Trading cycle result", result=result)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Trading bot stopped by user")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


def run():
    """Run the trading bot"""
    return asyncio.run(main())


if __name__ == "__main__":
    exit(run())