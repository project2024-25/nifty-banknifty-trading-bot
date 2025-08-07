#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.base_strategy import MarketData
from src.intelligence.dashboard_simple import SimpleMarketDashboard


async def test_simple_dashboard():
    print("=" * 80)
    print("TESTING MARKET CONDITIONS DASHBOARD (WINDOWS COMPATIBLE)")
    print("=" * 80)
    
    # Initialize dashboard
    dashboard = SimpleMarketDashboard(capital=1000000)
    
    # Test scenario
    market_data = MarketData(
        symbol="NIFTY", 
        spot_price=24000.0, 
        iv=35.0,
        volume=650000, 
        oi=110000, 
        last_updated=datetime.now()
    )
    
    try:
        print("[INFO] Updating dashboard with market data...")
        metrics = await dashboard.update_dashboard(market_data)
        
        print("\n[SUCCESS] Dashboard updated! Displaying results...\n")
        
        # Display the dashboard
        dashboard_display = dashboard.display_dashboard(metrics)
        print(dashboard_display)
        
        # Show additional summaries
        print(f"\n[REGIME SUMMARY]")
        print("-" * 30)
        regime_summary = dashboard.get_regime_summary()
        for key, value in regime_summary.items():
            print(f"{key.replace('_', ' ').title():<20}: {value}")
        
        print(f"\n[PERFORMANCE SUMMARY]")
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
        
    except Exception as e:
        print(f"[ERROR] Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_regime_changes():
    print(f"\n{'='*80}")
    print("TESTING REGIME CHANGES")
    print(f"{'='*80}")
    
    dashboard = SimpleMarketDashboard(capital=500000)
    
    # Test different IV levels to see regime changes
    test_scenarios = [
        {"name": "Low IV", "iv": 18.0, "volume": 400000},
        {"name": "High IV", "iv": 50.0, "volume": 800000},
        {"name": "Extreme IV", "iv": 65.0, "volume": 1000000},
        {"name": "Normal IV", "iv": 28.0, "volume": 500000}
    ]
    
    for scenario in test_scenarios:
        print(f"\n--- Testing {scenario['name']} (IV: {scenario['iv']}%) ---")
        
        market_data = MarketData(
            symbol="NIFTY",
            spot_price=24000.0,
            iv=scenario['iv'],
            volume=scenario['volume'],
            oi=100000,
            last_updated=datetime.now()
        )
        
        try:
            metrics = await dashboard.update_dashboard(market_data)
            
            print(f"Regime: {metrics.market_conditions.regime.value}")
            print(f"Volatility: {metrics.market_conditions.volatility_regime.value}")
            print(f"Strategies: {len(metrics.strategy_allocations)}")
            print(f"Signals: {metrics.active_signals_count}")
            print(f"Confidence: {metrics.confidence_score:.1%}")
            
        except Exception as e:
            print(f"[ERROR] Failed to test {scenario['name']}: {e}")


if __name__ == "__main__":
    asyncio.run(test_simple_dashboard())
    asyncio.run(test_regime_changes())