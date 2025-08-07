#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.base_strategy import MarketData
from src.core.adaptive_trading_engine import AdaptiveTradingEngine
from src.intelligence.dynamic_allocator import AllocationMode


async def test_adaptive_trading_engine():
    print("=" * 80)
    print("TESTING ADAPTIVE TRADING ENGINE")
    print("=" * 80)
    
    # Initialize adaptive trading engine
    engine = AdaptiveTradingEngine(initial_capital=1000000)
    
    try:
        # Initialize engine
        print("\n[STEP 1] Initializing Adaptive Trading Engine...")
        await engine.initialize()
        print("[SUCCESS] Engine initialized!")
        
        # Test different trading modes
        modes = [
            {"name": "Regime-Based Mode", "regime_intelligence": True},
            {"name": "Traditional Mode", "regime_intelligence": False}
        ]
        
        for mode in modes:
            print(f"\n{'='*60}")
            print(f"TESTING {mode['name'].upper()}")
            print(f"{'='*60}")
            
            # Configure engine mode
            engine.update_config({
                'enable_regime_intelligence': mode['regime_intelligence'],
                'allocation_mode': AllocationMode.REGIME_ADAPTIVE,
                'min_confidence_threshold': 0.5  # Lower threshold for testing
            })
            
            # Show engine status before trading
            status = engine.get_adaptive_status()
            print(f"\nEngine Status:")
            print(f"  Mode: {status['mode']}")
            print(f"  Active: {status['active']}")
            print(f"  Paper Trading: {status['paper_trading']}")
            print(f"  Initial Capital: Rs.{status['initial_capital']:,}")
            
            # Execute trading cycles
            print(f"\n[TESTING] Running 3 trading cycles in {mode['name']}...")
            
            for cycle in range(1, 4):
                print(f"\n--- Trading Cycle {cycle} ---")
                
                try:
                    # Execute trading cycle
                    result = await engine.execute_adaptive_trading_cycle()
                    
                    print(f"Cycle Result:")
                    print(f"  Status: {result.get('status')}")
                    
                    if result.get('status') == 'success':
                        if mode['regime_intelligence']:
                            # Regime-based results
                            print(f"  Mode: {result.get('mode')}")
                            print(f"  Symbols Processed: {result.get('symbols_processed', 0)}")
                            print(f"  Regimes Detected: {result.get('regimes_detected', {})}")
                            print(f"  Strategies Selected: {result.get('strategies_selected', {})}")
                            print(f"  Signals Generated: {result.get('signals_generated', 0)}")
                            print(f"  Trades Executed: {result.get('trades_executed', 0)}")
                            print(f"  Capital Deployed: Rs.{result.get('total_capital_deployed', 0):,.2f}")
                            print(f"  Risk Utilization: {result.get('risk_utilization', 0):.1%}")
                        else:
                            # Traditional results
                            print(f"  Mode: {result.get('mode')}")
                            print(f"  Signals Generated: {result.get('signals_generated', 0)}")
                            print(f"  Signals Validated: {result.get('signals_validated', 0)}")
                            print(f"  Trades Executed: {result.get('trades_executed', 0)}")
                    
                    # Brief pause between cycles
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"  [ERROR] Cycle {cycle} failed: {e}")
        
        # Test dashboard functionality
        print(f"\n{'='*60}")
        print("TESTING DASHBOARD INTEGRATION")
        print(f"{'='*60}")
        
        try:
            # Switch back to regime mode for dashboard test
            engine.switch_to_regime_mode()
            
            # Run one more cycle to populate dashboard
            await engine.execute_adaptive_trading_cycle()
            
            # Get dashboard display
            dashboard_display = await engine.get_dashboard_display()
            print(f"\nDashboard Display:")
            print(dashboard_display)
            
        except Exception as e:
            print(f"[ERROR] Dashboard test failed: {e}")
        
        # Test final status
        print(f"\n{'='*60}")
        print("FINAL ENGINE STATUS")
        print(f"{'='*60}")
        
        final_status = engine.get_adaptive_status()
        
        print(f"\nGeneral Status:")
        print(f"  Active: {final_status['active']}")
        print(f"  Mode: {final_status['mode']}")
        print(f"  Open Positions: {final_status['open_positions']}")
        print(f"  Daily P&L: Rs.{final_status['daily_pnl']:,.2f}")
        
        if 'regime_intelligence' in final_status:
            ri = final_status['regime_intelligence']
            if ri:
                print(f"\nRegime Intelligence:")
                print(f"  Current Regime: {ri.get('current_regime', 'N/A')}")
                print(f"  Volatility Regime: {ri.get('volatility_regime', 'N/A')}")
                print(f"  Trend Direction: {ri.get('trend_direction', 'N/A')}")
                print(f"  Detection Confidence: {ri.get('detection_confidence', 0):.1%}")
                print(f"  Strategies Selected: {ri.get('strategies_selected', 0)}")
                print(f"  Active Signals: {ri.get('active_signals', 0)}")
        
        if 'portfolio' in final_status:
            portfolio = final_status['portfolio']
            print(f"\nPortfolio Status:")
            print(f"  Total Positions: {portfolio.get('total_positions', 0)}")
            print(f"  Capital Utilization: {portfolio.get('utilization', {}).get('capital', 0):.1%}")
            print(f"  Risk Utilization: {portfolio.get('utilization', {}).get('risk', 0):.1%}")
        
        print(f"\n[SUCCESS] Adaptive Trading Engine test completed!")
        
    except Exception as e:
        print(f"[ERROR] Engine test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_regime_switching():
    print(f"\n{'='*80}")
    print("TESTING REGIME SWITCHING FUNCTIONALITY")
    print(f"{'='*80}")
    
    engine = AdaptiveTradingEngine(initial_capital=500000)
    await engine.initialize()
    
    # Test switching between modes
    modes_to_test = [
        ("Regime Intelligence", engine.switch_to_regime_mode),
        ("Traditional", engine.switch_to_traditional_mode),
        ("Back to Regime", engine.switch_to_regime_mode)
    ]
    
    for mode_name, switch_func in modes_to_test:
        print(f"\n--- Switching to {mode_name} ---")
        
        # Switch mode
        switch_func()
        
        # Execute one cycle
        result = await engine.execute_adaptive_trading_cycle()
        
        # Show results
        status = engine.get_adaptive_status()
        print(f"Current Mode: {status['mode']}")
        print(f"Cycle Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            if status['mode'] == 'adaptive':
                print(f"Regimes Detected: {result.get('regimes_detected', {})}")
            else:
                print(f"Traditional Signals: {result.get('signals_generated', 0)}")


async def test_configuration_changes():
    print(f"\n{'='*80}")
    print("TESTING CONFIGURATION CHANGES")
    print(f"{'='*80}")
    
    engine = AdaptiveTradingEngine()
    await engine.initialize()
    
    # Test different configurations
    configs_to_test = [
        {
            "name": "Conservative",
            "config": {
                'min_confidence_threshold': 0.8,
                'max_loss_per_trade': 5000,
                'allocation_mode': AllocationMode.EQUAL_WEIGHT
            }
        },
        {
            "name": "Moderate",
            "config": {
                'min_confidence_threshold': 0.6,
                'max_loss_per_trade': 10000,
                'allocation_mode': AllocationMode.CONFIDENCE_WEIGHTED
            }
        },
        {
            "name": "Aggressive",
            "config": {
                'min_confidence_threshold': 0.4,
                'max_loss_per_trade': 20000,
                'allocation_mode': AllocationMode.KELLY_CRITERION
            }
        }
    ]
    
    for config_test in configs_to_test:
        print(f"\n--- Testing {config_test['name']} Configuration ---")
        
        # Update configuration
        engine.update_config(config_test['config'])
        
        # Execute cycle
        result = await engine.execute_adaptive_trading_cycle()
        
        # Show results
        print(f"Configuration: {config_test['name']}")
        print(f"Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"Trades Executed: {result.get('trades_executed', 0)}")


if __name__ == "__main__":
    asyncio.run(test_adaptive_trading_engine())
    asyncio.run(test_regime_switching())
    asyncio.run(test_configuration_changes())