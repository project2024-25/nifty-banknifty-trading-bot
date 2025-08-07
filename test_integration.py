#!/usr/bin/env python3
"""
Complete System Integration Test
Tests all components working together
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_complete_integration():
    """Test all system components"""
    print("=" * 60)
    print("COMPLETE SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    try:
        from src.utils.config import get_config, validate_config
        
        if validate_config():
            config = get_config()
            print(f"   ✅ Configuration valid")
            print(f"   📊 Capital: {config.trading_capital:,}")
            print(f"   📈 Paper trading: {config.enable_paper_trading}")
            results['config'] = 'PASS'
        else:
            print("   ❌ Configuration invalid")
            results['config'] = 'FAIL'
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        results['config'] = 'ERROR'
    
    # Test 2: Database Connection
    print("\n2. Testing Database Connection...")
    try:
        from supabase import create_client
        
        supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_KEY')
        )
        
        result = supabase.table('trades').select('count', count='exact').execute()
        print(f"   ✅ Database connected")
        print(f"   📊 Tables accessible: trades ({result.count} records)")
        
        # Test other tables
        tables = ['positions', 'signals', 'performance_metrics']
        for table in tables:
            result = supabase.table(table).select('count', count='exact').execute()
            print(f"   📊 {table}: {result.count} records")
        
        results['database'] = 'PASS'
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        results['database'] = 'ERROR'
    
    # Test 3: Telegram Bot
    print("\n3. Testing Telegram Bot...")
    try:
        from telegram import Bot
        
        bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        me = await bot.get_me()
        
        print(f"   ✅ Bot connected: @{me.username}")
        print(f"   🤖 Bot name: {me.first_name}")
        print(f"   🔐 User ID authorized: {os.getenv('TELEGRAM_USER_ID')}")
        results['telegram'] = 'PASS'
    except Exception as e:
        print(f"   ❌ Telegram error: {e}")
        results['telegram'] = 'ERROR'
    
    # Test 4: Trading Engine
    print("\n4. Testing Trading Engine...")
    try:
        from src.core.trading_engine import TradingEngine
        
        engine = TradingEngine()
        status = engine.get_status()
        
        print(f"   ✅ Trading engine initialized")
        print(f"   📈 Paper trading: {engine.paper_trading}")
        print(f"   🔄 Active: {status['active']}")
        print(f"   📊 Open positions: {status['open_positions']}")
        results['trading_engine'] = 'PASS'
    except Exception as e:
        print(f"   ❌ Trading engine error: {e}")
        results['trading_engine'] = 'ERROR'
    
    # Test 5: Paper Trading Cycle
    print("\n5. Testing Paper Trading Cycle...")
    try:
        from src.core.trading_engine import TradingEngine
        
        engine = TradingEngine()
        engine.paper_trading = True
        
        # Initialize engine
        await engine.initialize()
        
        # Run a trading cycle
        cycle_result = await engine.execute_trading_cycle()
        
        print(f"   ✅ Trading cycle completed")
        print(f"   📊 Status: {cycle_result['status']}")
        if 'signals_generated' in cycle_result:
            print(f"   📈 Signals generated: {cycle_result['signals_generated']}")
        results['paper_trading'] = 'PASS'
    except Exception as e:
        print(f"   ❌ Paper trading error: {e}")
        results['paper_trading'] = 'ERROR'
    
    # Test 6: Logging System
    print("\n6. Testing Logging System...")
    try:
        from src.utils.logger import get_logger
        
        logger = get_logger("integration_test")
        logger.info("Integration test log entry", test_id="INT001", status="success")
        
        print("   ✅ Logging system working")
        print("   📝 Check logs/ directory for output")
        results['logging'] = 'PASS'
    except Exception as e:
        print(f"   ❌ Logging error: {e}")
        results['logging'] = 'ERROR'
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r == 'PASS')
    total = len(results)
    
    for test_name, result in results.items():
        emoji = "✅" if result == 'PASS' else "❌"
        print(f"{emoji} {test_name.replace('_', ' ').title()}: {result}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 Ready for Phase 2 development!")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please review errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_integration())
    exit(0 if success else 1)