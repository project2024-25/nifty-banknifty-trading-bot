#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.base_strategy import MarketData
from src.core.adaptive_trading_engine import AdaptiveTradingEngine


async def test_simple_engine():
    print("TESTING BASIC ENGINE FUNCTIONALITY")
    print("=" * 50)
    
    # Create engine
    engine = AdaptiveTradingEngine(initial_capital=1000000)
    
    try:
        # Initialize
        await engine.initialize()
        print("✓ Engine initialized successfully")
        
        # Test configuration update
        engine.update_config({
            'enable_regime_intelligence': True,
            'min_confidence_threshold': 0.4
        })
        print("✓ Configuration updated")
        
        # Test status retrieval
        status = engine.get_adaptive_status()
        print(f"✓ Status retrieved - Mode: {status['mode']}, Active: {status['active']}")
        
        # Test mode switching
        engine.switch_to_traditional_mode()
        print("✓ Switched to traditional mode")
        
        engine.switch_to_regime_mode()
        print("✓ Switched to regime mode")
        
        # Test market data fetching directly
        market_data = await engine._fetch_market_data()
        print(f"✓ Market data fetched - {len(market_data)} symbols")
        
        for symbol, data in market_data.items():
            print(f"  {symbol}: Spot={data.spot_price}, IV={data.iv}%")
        
        # Test dashboard display (should show not initialized)
        dashboard = await engine.get_dashboard_display()
        print(f"✓ Dashboard display retrieved")
        print(f"  First line: {dashboard.split(chr(10))[0]}")
        
        print("\n[SUCCESS] All basic functionality working!")
        
    except Exception as e:
        print(f"[ERROR] Basic test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_simple_trading_cycle():
    print("\n\nTESTING SIMPLE TRADING CYCLE")
    print("=" * 50)
    
    engine = AdaptiveTradingEngine()
    await engine.initialize()
    
    # Configure for testing
    engine.update_config({
        'enable_regime_intelligence': True,
        'min_confidence_threshold': 0.3
    })
    
    # Mock market as open for testing
    original_is_market_open = engine._is_market_open
    def mock_market_open():
        return True
    engine._is_market_open = mock_market_open
    
    try:
        # Execute one cycle
        result = await engine.execute_adaptive_trading_cycle()
        
        print(f"Cycle Result: {result}")
        
        if result.get('status') == 'success':
            print("✓ Trading cycle executed successfully!")
        else:
            print(f"✗ Cycle failed or skipped: {result.get('status')}")
            
    except Exception as e:
        print(f"[ERROR] Trading cycle failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original method
        engine._is_market_open = original_is_market_open


if __name__ == "__main__":
    asyncio.run(test_simple_engine())
    asyncio.run(test_simple_trading_cycle())