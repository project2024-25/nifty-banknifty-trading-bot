#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.base_strategy import MarketData
from src.intelligence.dashboard import MarketConditionsDashboard


async def test_dashboard():
    print("=" * 80)
    print("TESTING MARKET CONDITIONS DASHBOARD")
    print("=" * 80)
    
    # Initialize dashboard
    dashboard = MarketConditionsDashboard(capital=1000000)
    
    # Test different market scenarios
    test_scenarios = [
        {
            "name": "Bull Market Scenario",
            "data": MarketData(
                symbol="NIFTY", spot_price=24500.0, iv=22.0,
                volume=650000, oi=110000, last_updated=datetime.now()
            )
        },
        {
            "name": "High Volatility Scenario", 
            "data": MarketData(
                symbol="NIFTY", spot_price=24000.0, iv=48.0,
                volume=850000, oi=130000, last_updated=datetime.now()
            )
        },
        {
            "name": "Low Volatility Scenario",
            "data": MarketData(
                symbol="NIFTY", spot_price=24200.0, iv=16.0,
                volume=420000, oi=85000, last_updated=datetime.now()
            )
        },
        {
            "name": "Uncertain Market Scenario",
            "data": MarketData(
                symbol="NIFTY", spot_price=23800.0, iv=55.0,
                volume=380000, oi=75000, last_updated=datetime.now()
            )
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*70}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"{'='*70}")
        
        try:
            # Update dashboard with new market data
            metrics = await dashboard.update_dashboard(scenario['data'])
            
            # Display the dashboard
            dashboard_display = dashboard.display_dashboard(metrics)
            print(dashboard_display)
            
            # Show additional summaries
            print(f"\n📋 REGIME SUMMARY")
            print("-" * 30)
            regime_summary = dashboard.get_regime_summary()
            for key, value in regime_summary.items():
                print(f"{key.replace('_', ' ').title():<20}: {value}")
            
            print(f"\n📊 PERFORMANCE SUMMARY")
            print("-" * 30)
            perf_summary = dashboard.get_strategy_performance_summary()
            for key, value in perf_summary.items():
                if isinstance(value, float):
                    if 'rate' in key or 'utilization' in key:
                        print(f"{key.replace('_', ' ').title():<20}: {value:.1%}")
                    else:
                        print(f"{key.replace('_', ' ').title():<20}: {value:,.2f}")
                else:
                    print(f"{key.replace('_', ' ').title():<20}: {value}")
            
            # Add delay between scenarios for realistic testing
            if i < len(test_scenarios):
                print(f"\n[Waiting 2 seconds before next scenario...]")
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"[ERROR] Failed to test scenario: {e}")
            import traceback
            traceback.print_exc()
    
    # Test historical trends
    print(f"\n{'='*80}")
    print("HISTORICAL TRENDS ANALYSIS")
    print(f"{'='*80}")
    
    try:
        trends = dashboard.get_historical_trends()
        if 'error' not in trends:
            print(f"📈 TREND ANALYSIS")
            print("-" * 30)
            for key, value in trends.items():
                if isinstance(value, float):
                    print(f"{key.replace('_', ' ').title():<25}: {value:.2f}")
                else:
                    print(f"{key.replace('_', ' ').title():<25}: {value}")
        else:
            print(f"[INFO] {trends['error']}")
    except Exception as e:
        print(f"[ERROR] Trend analysis failed: {e}")
    
    print(f"\n{'='*80}")
    print("DASHBOARD TESTING COMPLETED")
    print(f"{'='*80}")
    
    return dashboard


async def demo_real_time_dashboard():
    print(f"\n{'='*80}")
    print("DEMO: REAL-TIME DASHBOARD UPDATES")
    print(f"{'='*80}")
    
    dashboard = MarketConditionsDashboard(capital=500000)
    
    # Simulate real-time market data changes
    base_data = MarketData(
        symbol="NIFTY", spot_price=24000.0, iv=30.0,
        volume=500000, oi=100000, last_updated=datetime.now()
    )
    
    # Simulate IV changes over time
    iv_changes = [25.0, 35.0, 45.0, 55.0, 40.0, 30.0, 20.0]
    
    for i, new_iv in enumerate(iv_changes, 1):
        print(f"\n--- Update {i}: IV changing to {new_iv}% ---")
        
        # Update market data
        base_data.iv = new_iv
        base_data.volume = base_data.volume + (i * 50000)  # Simulate volume increase
        base_data.last_updated = datetime.now()
        
        try:
            # Update dashboard
            metrics = await dashboard.update_dashboard(base_data)
            
            # Show key changes
            print(f"Regime: {metrics.market_conditions.regime.value}")
            print(f"Volatility: {metrics.market_conditions.volatility_regime.value}")
            print(f"Strategies: {len(metrics.strategy_allocations)}")
            print(f"Signals: {metrics.active_signals_count}")
            print(f"Confidence: {metrics.confidence_score:.1%}")
            
            if i < len(iv_changes):
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"[ERROR] Update {i} failed: {e}")
    
    # Final dashboard display
    print(f"\n{'='*50}")
    print("FINAL DASHBOARD STATE")
    print(f"{'='*50}")
    final_display = dashboard.display_dashboard()
    print(final_display)


if __name__ == "__main__":
    # Run main dashboard test
    dashboard = asyncio.run(test_dashboard())
    
    # Run real-time demo
    asyncio.run(demo_real_time_dashboard())