#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.base_strategy import MarketData
from src.intelligence.strategy_selector import AdaptiveStrategySelector


async def test_adaptive_strategy_selection():
    print("=" * 80)
    print("TESTING ADAPTIVE STRATEGY SELECTION")
    print("=" * 80)
    
    selector = AdaptiveStrategySelector()
    
    # Test different market scenarios
    scenarios = [
        {
            "name": "Bull Trending Market (Low Vol)",
            "data": MarketData(
                symbol="NIFTY", spot_price=24000.0, iv=20.0,
                volume=600000, oi=100000, last_updated=datetime.now()
            )
        },
        {
            "name": "High Volatility Market", 
            "data": MarketData(
                symbol="NIFTY", spot_price=24000.0, iv=45.0,
                volume=800000, oi=120000, last_updated=datetime.now()
            )
        },
        {
            "name": "Sideways Low Vol Market",
            "data": MarketData(
                symbol="NIFTY", spot_price=24000.0, iv=18.0,
                volume=400000, oi=80000, last_updated=datetime.now()
            )
        },
        {
            "name": "Medium Volatility Market",
            "data": MarketData(
                symbol="NIFTY", spot_price=24000.0, iv=30.0,
                volume=500000, oi=100000, last_updated=datetime.now()
            )
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'='*70}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"Spot: {scenario['data'].spot_price}, IV: {scenario['data'].iv}%")
        print(f"{'='*70}")
        
        try:
            # Get strategy allocations
            allocations = await selector.select_strategies(scenario['data'])
            
            if allocations:
                print(f"\n✓ Selected {len(allocations)} strategies:")
                print(f"{'Strategy':<20} {'Weight':<10} {'Max Pos':<8} {'Priority':<8}")
                print("-" * 50)
                
                for allocation in allocations:
                    print(f"{allocation.strategy_name:<20} {allocation.allocation_weight:<10.1%} "
                          f"{allocation.max_positions:<8} {allocation.priority:<8}")
                
                # Generate adaptive signals
                print(f"\n🔍 Generating adaptive signals...")
                signals = await selector.generate_adaptive_signals(scenario['data'])
                
                if signals:
                    print(f"✓ Generated {len(signals)} total signals")
                    
                    print(f"\nTop 3 Signals:")
                    for i, signal in enumerate(signals[:3], 1):
                        print(f"  {i}. {signal.strategy_name}")
                        print(f"     Confidence: {signal.confidence_score:.1%}")
                        print(f"     Max Profit: Rs.{signal.max_profit}")
                        print(f"     Max Loss: Rs.{signal.max_loss}")
                        print(f"     Legs: {len(signal.legs)}")
                        
                        if signal.metadata:
                            weight = signal.metadata.get('allocation_weight', 0)
                            priority = signal.metadata.get('selection_priority', 0)
                            print(f"     Allocation Weight: {weight:.1%}, Priority: {priority}")
                        print()
                else:
                    print("⚠️  No signals generated despite strategy selection")
                    
            else:
                print("⚠️  No strategies selected for this market scenario")
                
        except Exception as e:
            print(f"❌ Error testing scenario: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("ADAPTIVE STRATEGY SELECTION TESTING COMPLETED")
    print(f"{'='*80}")


async def test_market_regime_detection():
    print("\n" + "=" * 80)
    print("TESTING MARKET REGIME DETECTION")
    print("=" * 80)
    
    selector = AdaptiveStrategySelector()
    
    # Test different market conditions for regime detection
    test_conditions = [
        {"name": "High IV Bull Market", "spot": 24000, "iv": 45},
        {"name": "Low IV Bear Market", "spot": 23000, "iv": 15},
        {"name": "Sideways Market", "spot": 24000, "iv": 25},
        {"name": "Extreme Vol Market", "spot": 24000, "iv": 60},
    ]
    
    for condition in test_conditions:
        market_data = MarketData(
            symbol="NIFTY",
            spot_price=condition["spot"],
            iv=condition["iv"],
            volume=500000,
            oi=100000,
            last_updated=datetime.now()
        )
        
        print(f"\n--- {condition['name']} ---")
        print(f"Spot: {condition['spot']}, IV: {condition['iv']}%")
        
        try:
            # Get market conditions
            market_conditions = selector.regime_detector.detect_regime(market_data)
            
            print(f"Detected Regime: {market_conditions.regime.value}")
            print(f"Volatility Regime: {market_conditions.volatility_regime.value}")
            print(f"Trend Direction: {market_conditions.trend_direction}")
            print(f"Trend Strength: {market_conditions.trend_strength.value}")
            print(f"Confidence: {market_conditions.confidence_score:.1%}")
            print(f"IV Percentile: {market_conditions.iv_percentile:.1f}")
            print(f"Momentum Score: {market_conditions.momentum_score:.2f}")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_adaptive_strategy_selection())
    asyncio.run(test_market_regime_detection())