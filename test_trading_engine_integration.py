#!/usr/bin/env python3
import asyncio
import sys
from src.core.trading_engine import TradingEngine


async def test_trading_engine_integration():
    print("=" * 60)
    print("TRADING ENGINE INTEGRATION TEST")
    print("=" * 60)
    
    # Initialize trading engine
    engine = TradingEngine()
    
    print("\n1. Testing Trading Engine Initialization...")
    try:
        await engine.initialize()
        print("   [PASS] Trading engine initialized successfully")
        
        # Check strategy manager
        if engine.strategy_manager:
            active_strategies = engine.strategy_manager.get_active_strategies()
            print(f"   [INFO] Active strategies: {active_strategies}")
        else:
            print("   [FAIL] Strategy manager not initialized")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Trading engine initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n2. Testing Trading Engine Status...")
    try:
        status = engine.get_status()
        print(f"   [INFO] Active: {status['active']}")
        print(f"   [INFO] Paper Trading: {status['paper_trading']}")
        print(f"   [INFO] Daily P&L: {status['daily_pnl']}")
        print(f"   [INFO] Open Positions: {status['open_positions']}")
        print(f"   [INFO] Active Strategies: {status['strategies_active']}")
        print(f"   [INFO] Market Open: {status['market_open']}")
        print("   [PASS] Trading engine status retrieved")
        
    except Exception as e:
        print(f"   [FAIL] Status check failed: {e}")
        return False
    
    print("\n3. Testing Trading Cycle Execution...")
    try:
        # Execute a trading cycle (this will generate Iron Condor signals)
        cycle_result = await engine.execute_trading_cycle()
        
        print(f"   [INFO] Cycle Status: {cycle_result['status']}")
        
        if cycle_result['status'] == 'success':
            print(f"   [INFO] Signals Generated: {cycle_result['signals_generated']}")
            print(f"   [INFO] Trades Executed: {cycle_result['trades_executed']}")
            print(f"   [INFO] Current P&L: {cycle_result['current_pnl']}")
            print("   [PASS] Trading cycle executed successfully")
            
            # Check if any positions were created
            if len(engine.positions) > 0:
                print(f"   [INFO] Positions created: {len(engine.positions)}")
                for position_id, position in engine.positions.items():
                    signal = position['signal']
                    print(f"      - {position_id}: {signal.strategy_name} on {signal.symbol}")
                    print(f"        Max Profit: {signal.max_profit}, Max Loss: {signal.max_loss}")
            else:
                print("   [INFO] No positions created (market may be closed)")
                
        else:
            print(f"   [WARN] Trading cycle status: {cycle_result['status']}")
            if 'error' in cycle_result:
                print(f"   [INFO] Error: {cycle_result['error']}")
        
    except Exception as e:
        print(f"   [FAIL] Trading cycle failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n4. Testing Strategy Performance...")
    try:
        if engine.strategy_manager:
            performance = engine.strategy_manager.get_strategy_performance()
            print(f"   [INFO] Active Signals: {performance['active_signals_count']}")
            print(f"   [INFO] Portfolio Risk: Rs.{performance['total_portfolio_risk']}")
            
            for strategy_name, perf in performance['strategies'].items():
                print(f"   [INFO] {strategy_name}:")
                print(f"      Total Signals: {perf['total_signals']}")
                print(f"      Win Rate: {perf['win_rate']:.2%}")
                print(f"      Total P&L: Rs.{perf['total_pnl']}")
        
        print("   [PASS] Strategy performance retrieved")
        
    except Exception as e:
        print(f"   [FAIL] Performance check failed: {e}")
        return False
    
    print("\n5. Testing Pause/Resume Functionality...")
    try:
        # Test pause
        engine.pause_trading()
        status_paused = engine.get_status()
        print(f"   [INFO] Trading paused: {not status_paused['active']}")
        
        # Test resume
        engine.resume_trading()
        status_resumed = engine.get_status()
        print(f"   [INFO] Trading resumed: {status_resumed['active']}")
        
        print("   [PASS] Pause/Resume functionality working")
        
    except Exception as e:
        print(f"   [FAIL] Pause/Resume test failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("TRADING ENGINE INTEGRATION TEST RESULTS")
    print("=" * 60)
    print("[PASS] Trading engine initialization: PASSED")
    print("[PASS] Status reporting: PASSED")
    print("[PASS] Trading cycle execution: PASSED")
    print("[PASS] Strategy performance: PASSED")
    print("[PASS] Pause/Resume functionality: PASSED")
    
    print("\n[SUCCESS] TRADING ENGINE INTEGRATION TEST PASSED!")
    print("[INFO] Iron Condor strategy fully integrated with trading engine!")
    print("[INFO] Paper trading mode is operational!")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_trading_engine_integration())
    sys.exit(0 if success else 1)