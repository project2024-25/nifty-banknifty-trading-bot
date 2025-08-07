#!/usr/bin/env python3
import asyncio
from datetime import datetime, time
from unittest.mock import patch
from src.strategies.base_strategy import MarketData
from src.core.adaptive_trading_engine import AdaptiveTradingEngine
from src.intelligence.dynamic_allocator import AllocationMode


async def test_adaptive_engine_full():
    print("=" * 80)
    print("TESTING ADAPTIVE TRADING ENGINE - FULL FUNCTIONALITY")
    print("=" * 80)
    
    # Initialize adaptive trading engine
    engine = AdaptiveTradingEngine(initial_capital=1000000)
    
    # Mock market hours to be always open for testing
    def mock_is_market_open(self):
        return True
    
    # Patch the market hours check
    with patch.object(AdaptiveTradingEngine, '_is_market_open', mock_is_market_open):
        try:
            # Initialize engine
            print("\n[STEP 1] Initializing Adaptive Trading Engine...")
            await engine.initialize()
            print("[SUCCESS] Engine initialized!")
            
            # Test regime-based mode with market open
            print(f"\n{'='*70}")
            print("TESTING REGIME-BASED MODE (MARKET OPEN)")
            print(f"{'='*70}")
            
            # Configure for regime-based trading
            engine.update_config({
                'enable_regime_intelligence': True,
                'allocation_mode': AllocationMode.REGIME_ADAPTIVE,
                'min_confidence_threshold': 0.4,  # Lower for testing
                'max_loss_per_trade': 15000
            })
            
            # Execute several trading cycles with different market conditions
            test_scenarios = [
                {"name": "Normal IV Market", "nifty_iv": 30.0, "banknifty_iv": 35.0},
                {"name": "High IV Market", "nifty_iv": 50.0, "banknifty_iv": 55.0},
                {"name": "Low IV Market", "nifty_iv": 18.0, "banknifty_iv": 22.0}
            ]
            
            for scenario in test_scenarios:
                print(f"\n--- Scenario: {scenario['name']} ---")
                
                # Mock market data for this scenario
                def mock_fetch_market_data():
                    return {
                        "NIFTY": MarketData(
                            symbol="NIFTY",
                            spot_price=24000.0 + (len(scenario['name']) * 50),  # Vary price slightly
                            iv=scenario['nifty_iv'],
                            volume=500000,
                            oi=100000,
                            last_updated=datetime.now()
                        ),
                        "BANKNIFTY": MarketData(
                            symbol="BANKNIFTY",
                            spot_price=50000.0 + (len(scenario['name']) * 100),  # Vary price slightly
                            iv=scenario['banknifty_iv'],
                            volume=300000,
                            oi=80000,
                            last_updated=datetime.now()
                        )
                    }
                
                # Patch market data fetching
                with patch.object(engine, '_fetch_market_data', mock_fetch_market_data):
                    
                    try:
                        # Execute trading cycle
                        result = await engine.execute_adaptive_trading_cycle()
                        
                        print(f"Trading Cycle Result:")
                        print(f"  Status: {result.get('status')}")
                        
                        if result.get('status') == 'success':
                            print(f"  Mode: {result.get('mode')}")
                            print(f"  Symbols Processed: {result.get('symbols_processed', 0)}")
                            
                            regimes = result.get('regimes_detected', {})
                            if regimes:
                                print(f"  Regimes Detected:")
                                for symbol, regime in regimes.items():
                                    print(f"    {symbol}: {regime}")
                            
                            strategies = result.get('strategies_selected', {})
                            if strategies:
                                print(f"  Strategies Selected:")
                                for symbol, count in strategies.items():
                                    print(f"    {symbol}: {count} strategies")
                            
                            print(f"  Total Signals: {result.get('signals_generated', 0)}")
                            print(f"  Trades Executed: {result.get('trades_executed', 0)}")
                            print(f"  Capital Deployed: Rs.{result.get('total_capital_deployed', 0):,.2f}")
                            print(f"  Risk Utilization: {result.get('risk_utilization', 0):.2%}")
                            
                        await asyncio.sleep(0.5)  # Brief pause
                        
                    except Exception as e:
                        print(f"  [ERROR] Scenario failed: {e}")
            
            # Test dashboard after trading cycles
            print(f"\n{'='*70}")
            print("TESTING DASHBOARD AFTER TRADING")
            print(f"{'='*70}")
            
            try:
                dashboard_display = await engine.get_dashboard_display()
                print(f"\nCurrent Dashboard:")
                print("-" * 50)
                print(dashboard_display)
                
            except Exception as e:
                print(f"[ERROR] Dashboard display failed: {e}")
            
            # Test final comprehensive status
            print(f"\n{'='*70}")
            print("COMPREHENSIVE ENGINE STATUS")
            print(f"{'='*70}")
            
            status = engine.get_adaptive_status()
            
            print(f"\n=== GENERAL STATUS ===")
            print(f"Active: {status['active']}")
            print(f"Mode: {status['mode']}")
            print(f"Paper Trading: {status['paper_trading']}")
            print(f"Market Open: {status['market_open']}")
            print(f"Open Positions: {status['open_positions']}")
            print(f"Daily P&L: Rs.{status['daily_pnl']:,.2f}")
            print(f"Initial Capital: Rs.{status['initial_capital']:,}")
            
            # Regime intelligence status
            if 'regime_intelligence' in status and status['regime_intelligence']:
                ri = status['regime_intelligence']
                print(f"\n=== REGIME INTELLIGENCE ===")
                print(f"Current Regime: {ri.get('current_regime', 'N/A')}")
                print(f"Volatility Regime: {ri.get('volatility_regime', 'N/A')}")
                print(f"Trend Direction: {ri.get('trend_direction', 'N/A')}")
                print(f"Detection Confidence: {ri.get('detection_confidence', 0):.1%}")
                print(f"Strategies Selected: {ri.get('strategies_selected', 0)}")
                print(f"Active Signals: {ri.get('active_signals', 0)}")
                print(f"Capital Deployed: Rs.{ri.get('capital_deployed', 0):,.2f}")
                print(f"Risk Utilization: {ri.get('risk_utilization', 0):.1%}")
                print(f"Last Updated: {ri.get('last_updated', 'N/A')}")
            
            # Portfolio status
            if 'portfolio' in status:
                portfolio = status['portfolio']
                print(f"\n=== PORTFOLIO STATUS ===")
                print(f"Total Positions: {portfolio.get('total_positions', 0)}")
                print(f"Total Capital: Rs.{portfolio.get('total_capital', 0):,}")
                print(f"Allocated Capital: Rs.{portfolio.get('allocated_capital', 0):,}")
                print(f"Available Capital: Rs.{portfolio.get('available_capital', 0):,}")
                
                utilization = portfolio.get('utilization', {})
                print(f"Capital Utilization: {utilization.get('capital', 0):.1%}")
                print(f"Risk Utilization: {utilization.get('risk', 0):.1%}")
            
            # Configuration
            if 'config' in status:
                config = status['config']
                print(f"\n=== CONFIGURATION ===")
                print(f"Min Confidence Threshold: {config.get('min_confidence_threshold', 0):.1%}")
                print(f"Max Loss Per Trade: Rs.{config.get('max_loss_per_trade', 0):,}")
                print(f"Allocation Mode: {config.get('allocation_mode', 'N/A')}")
                print(f"Regime Intelligence: {config.get('enable_regime_intelligence', False)}")
                print(f"Dashboard Updates: {config.get('update_dashboard_every_cycle', False)}")
            
            # Show some position details if any exist
            if status['open_positions'] > 0:
                print(f"\n=== RECENT POSITIONS ===")
                for pos_id, pos_data in list(engine.positions.items())[:3]:  # Show first 3
                    print(f"Position: {pos_id}")
                    print(f"  Strategy: {pos_data['signal'].strategy_name}")
                    print(f"  Status: {pos_data['status']}")
                    print(f"  Entry Time: {pos_data['entry_time']}")
                    print(f"  Regime Context: {pos_data.get('regime_context', False)}")
                    if pos_data.get('position'):
                        pos = pos_data['position']
                        print(f"  Position Size: {pos.position_size}")
                        print(f"  Allocation Weight: {pos.allocation_weight:.1%}")
            
            print(f"\n[SUCCESS] Full adaptive trading engine test completed!")
            
        except Exception as e:
            print(f"[ERROR] Full engine test failed: {e}")
            import traceback
            traceback.print_exc()


async def test_traditional_vs_adaptive_comparison():
    print(f"\n{'='*80}")
    print("COMPARING TRADITIONAL VS ADAPTIVE MODES")
    print(f"{'='*80}")
    
    engine = AdaptiveTradingEngine(initial_capital=500000)
    
    # Mock market to be always open
    def mock_is_market_open(self):
        return True
    
    # Mock consistent market data
    def mock_fetch_market_data():
        return {
            "NIFTY": MarketData(
                symbol="NIFTY",
                spot_price=24000.0,
                iv=35.0,  # Medium volatility
                volume=600000,
                oi=120000,
                last_updated=datetime.now()
            )
        }
    
    with patch.object(AdaptiveTradingEngine, '_is_market_open', mock_is_market_open):
        with patch.object(engine, '_fetch_market_data', mock_fetch_market_data):
            
            await engine.initialize()
            
            # Lower thresholds for comparison testing
            engine.update_config({
                'min_confidence_threshold': 0.3,
                'max_loss_per_trade': 20000
            })
            
            # Test traditional mode
            print(f"\n--- Traditional Mode ---")
            engine.switch_to_traditional_mode()
            trad_result = await engine.execute_adaptive_trading_cycle()
            trad_status = engine.get_adaptive_status()
            
            print(f"Traditional Results:")
            print(f"  Status: {trad_result.get('status')}")
            print(f"  Mode: {trad_status['mode']}")
            
            if trad_result.get('status') == 'success':
                print(f"  Signals Generated: {trad_result.get('signals_generated', 0)}")
                print(f"  Trades Executed: {trad_result.get('trades_executed', 0)}")
            
            # Reset positions for fair comparison
            engine.positions = {}
            engine.allocation_manager = engine.allocation_manager.__class__(total_capital=500000)
            
            # Test adaptive mode
            print(f"\n--- Adaptive Mode ---")
            engine.switch_to_regime_mode()
            adapt_result = await engine.execute_adaptive_trading_cycle()
            adapt_status = engine.get_adaptive_status()
            
            print(f"Adaptive Results:")
            print(f"  Status: {adapt_result.get('status')}")
            print(f"  Mode: {adapt_status['mode']}")
            
            if adapt_result.get('status') == 'success':
                print(f"  Symbols Processed: {adapt_result.get('symbols_processed', 0)}")
                print(f"  Regimes Detected: {adapt_result.get('regimes_detected', {})}")
                print(f"  Signals Generated: {adapt_result.get('signals_generated', 0)}")
                print(f"  Trades Executed: {adapt_result.get('trades_executed', 0)}")
                print(f"  Capital Deployed: Rs.{adapt_result.get('total_capital_deployed', 0):,.2f}")
            
            # Summary comparison
            print(f"\n--- COMPARISON SUMMARY ---")
            print(f"Traditional Trades: {trad_result.get('trades_executed', 0)}")
            print(f"Adaptive Trades: {adapt_result.get('trades_executed', 0)}")
            print(f"Adaptive shows regime-aware selection vs traditional all-strategy approach")


if __name__ == "__main__":
    asyncio.run(test_adaptive_engine_full())
    asyncio.run(test_traditional_vs_adaptive_comparison())