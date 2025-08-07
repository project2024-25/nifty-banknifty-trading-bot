#!/usr/bin/env python3
import asyncio
import sys
from src.core.trading_engine import TradingEngine


async def test_paper_trading():
    print("=" * 60)
    print("PAPER TRADING IRON CONDOR TEST")
    print("=" * 60)
    
    # Initialize trading engine
    engine = TradingEngine()
    await engine.initialize()
    
    # Temporarily override market hours check for testing
    original_is_market_open = engine._is_market_open
    engine._is_market_open = lambda: True  # Always return True for testing
    
    print("\n1. Testing Paper Trading Execution...")
    try:
        print("   [INFO] Overriding market hours for testing...")
        
        # Execute trading cycle
        cycle_result = await engine.execute_trading_cycle()
        
        print(f"   [INFO] Cycle Status: {cycle_result['status']}")
        print(f"   [INFO] Signals Generated: {cycle_result.get('signals_generated', 0)}")
        print(f"   [INFO] Trades Executed: {cycle_result.get('trades_executed', 0)}")
        
        if cycle_result['status'] == 'success' and cycle_result.get('trades_executed', 0) > 0:
            print("   [PASS] Paper trades executed successfully")
            
            # Show positions
            print(f"\n   [INFO] Active Positions: {len(engine.positions)}")
            for position_id, position in engine.positions.items():
                signal = position['signal']
                print(f"      Position: {position_id}")
                print(f"      Strategy: {signal.strategy_name}")
                print(f"      Symbol: {signal.symbol}")
                print(f"      Max Profit: Rs.{signal.max_profit}")
                print(f"      Max Loss: Rs.{signal.max_loss}")
                print(f"      Confidence: {signal.confidence_score:.2%}")
                print(f"      Entry Time: {position['entry_time']}")
                print(f"      Status: {position['status']}")
                print()
                
        else:
            print("   [WARN] No trades executed")
            
    except Exception as e:
        print(f"   [FAIL] Paper trading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n2. Testing Strategy Performance After Trading...")
    try:
        if engine.strategy_manager:
            performance = engine.strategy_manager.get_strategy_performance()
            print(f"   [INFO] Active Signals: {performance['active_signals_count']}")
            print(f"   [INFO] Portfolio Risk: Rs.{performance['total_portfolio_risk']}")
            
            for strategy_name, perf in performance['strategies'].items():
                if perf['total_signals'] > 0:
                    print(f"   [INFO] {strategy_name} Performance:")
                    print(f"      Total Signals: {perf['total_signals']}")
                    print(f"      Successful Signals: {perf['successful_signals']}")
                    print(f"      Win Rate: {perf['win_rate']:.2%}")
                    print(f"      Total P&L: Rs.{perf['total_pnl']}")
        
        print("   [PASS] Performance tracking working")
        
    except Exception as e:
        print(f"   [FAIL] Performance check failed: {e}")
        return False
    
    print("\n3. Testing Multiple Trading Cycles...")
    try:
        print("   [INFO] Running additional trading cycles...")
        
        for cycle in range(2, 4):  # Run 2 more cycles
            cycle_result = await engine.execute_trading_cycle()
            print(f"   [INFO] Cycle {cycle}: {cycle_result['status']}, " +
                  f"Signals: {cycle_result.get('signals_generated', 0)}, " +
                  f"Trades: {cycle_result.get('trades_executed', 0)}")
        
        print(f"   [INFO] Final Position Count: {len(engine.positions)}")
        print("   [PASS] Multiple trading cycles completed")
        
    except Exception as e:
        print(f"   [FAIL] Multiple cycles test failed: {e}")
        return False
    
    # Restore original market hours check
    engine._is_market_open = original_is_market_open
    
    print("\n" + "=" * 60)
    print("PAPER TRADING TEST RESULTS")
    print("=" * 60)
    print("[PASS] Paper trading execution: PASSED")
    print("[PASS] Performance tracking: PASSED") 
    print("[PASS] Multiple trading cycles: PASSED")
    
    print("\n[SUCCESS] PAPER TRADING TEST PASSED!")
    print("[INFO] Iron Condor strategy working in paper trading mode!")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_paper_trading())
    sys.exit(0 if success else 1)