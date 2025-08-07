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
        print("[SUCCESS] Engine initialized successfully")
        
        # Test configuration update
        engine.update_config({
            'enable_regime_intelligence': True,
            'min_confidence_threshold': 0.4
        })
        print("[SUCCESS] Configuration updated")
        
        # Test status retrieval
        status = engine.get_adaptive_status()
        print(f"[SUCCESS] Status retrieved - Mode: {status['mode']}, Active: {status['active']}")
        
        # Test mode switching
        engine.switch_to_traditional_mode()
        print("[SUCCESS] Switched to traditional mode")
        
        engine.switch_to_regime_mode()
        print("[SUCCESS] Switched to regime mode")
        
        # Test market data fetching directly
        market_data = await engine._fetch_market_data()
        print(f"[SUCCESS] Market data fetched - {len(market_data)} symbols")
        
        for symbol, data in market_data.items():
            print(f"  {symbol}: Spot={data.spot_price}, IV={data.iv}%")
        
        # Test dashboard display (should show not initialized)
        dashboard = await engine.get_dashboard_display()
        print(f"[SUCCESS] Dashboard display retrieved")
        
        print("\n[SUCCESS] All basic functionality working!")
        
    except Exception as e:
        print(f"[ERROR] Basic test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_trading_cycle():
    print("\n\nTESTING TRADING CYCLE WITH MARKET OPEN")
    print("=" * 50)
    
    engine = AdaptiveTradingEngine()
    await engine.initialize()
    
    # Configure for testing
    engine.update_config({
        'enable_regime_intelligence': True,
        'min_confidence_threshold': 0.3
    })
    
    # Mock market as open for testing
    def mock_market_open():
        return True
    engine._is_market_open = mock_market_open
    
    try:
        print("[INFO] Executing adaptive trading cycle...")
        
        # Execute one cycle
        result = await engine.execute_adaptive_trading_cycle()
        
        print(f"[RESULT] Cycle Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print("[SUCCESS] Trading cycle executed successfully!")
            print(f"  Mode: {result.get('mode', 'N/A')}")
            print(f"  Symbols Processed: {result.get('symbols_processed', 0)}")
            print(f"  Regimes Detected: {result.get('regimes_detected', {})}")
            print(f"  Signals Generated: {result.get('signals_generated', 0)}")
            print(f"  Trades Executed: {result.get('trades_executed', 0)}")
            print(f"  Capital Deployed: {result.get('total_capital_deployed', 0):,.2f}")
        elif result.get('status') == 'error':
            print(f"[ERROR] Cycle error: {result.get('error', 'Unknown error')}")
        else:
            print(f"[INFO] Cycle skipped: {result.get('status')}")
            
        # Test status after cycle
        final_status = engine.get_adaptive_status()
        print(f"\n[STATUS] After trading cycle:")
        print(f"  Open Positions: {final_status.get('open_positions', 0)}")
        print(f"  Daily P&L: Rs.{final_status.get('daily_pnl', 0):,.2f}")
        
        if 'regime_intelligence' in final_status and final_status['regime_intelligence']:
            ri = final_status['regime_intelligence']
            print(f"  Current Regime: {ri.get('current_regime', 'N/A')}")
            print(f"  Detection Confidence: {ri.get('detection_confidence', 0):.1%}")
            
    except Exception as e:
        print(f"[ERROR] Trading cycle failed: {e}")
        import traceback
        traceback.print_exc()


async def test_traditional_vs_adaptive():
    print("\n\nTESTING TRADITIONAL VS ADAPTIVE COMPARISON")
    print("=" * 55)
    
    engine = AdaptiveTradingEngine(initial_capital=500000)
    await engine.initialize()
    
    # Mock market open
    def mock_market_open():
        return True
    engine._is_market_open = mock_market_open
    
    # Test traditional mode
    print("\n--- Traditional Mode Test ---")
    engine.switch_to_traditional_mode()
    engine.update_config({'min_confidence_threshold': 0.3})
    
    try:
        trad_result = await engine.execute_adaptive_trading_cycle()
        print(f"Traditional Result: {trad_result.get('status')}")
        if trad_result.get('status') == 'success':
            print(f"  Signals: {trad_result.get('signals_generated', 0)}")
            print(f"  Trades: {trad_result.get('trades_executed', 0)}")
    except Exception as e:
        print(f"[ERROR] Traditional mode failed: {e}")
    
    # Reset for fair comparison
    engine.positions = {}
    
    # Test adaptive mode  
    print("\n--- Adaptive Mode Test ---")
    engine.switch_to_regime_mode()
    
    try:
        adapt_result = await engine.execute_adaptive_trading_cycle()
        print(f"Adaptive Result: {adapt_result.get('status')}")
        if adapt_result.get('status') == 'success':
            print(f"  Mode: {adapt_result.get('mode')}")
            print(f"  Regimes: {adapt_result.get('regimes_detected', {})}")
            print(f"  Signals: {adapt_result.get('signals_generated', 0)}")
            print(f"  Trades: {adapt_result.get('trades_executed', 0)}")
    except Exception as e:
        print(f"[ERROR] Adaptive mode failed: {e}")
    
    print("\n[INFO] Comparison test completed")


if __name__ == "__main__":
    asyncio.run(test_simple_engine())
    asyncio.run(test_trading_cycle())
    asyncio.run(test_traditional_vs_adaptive())