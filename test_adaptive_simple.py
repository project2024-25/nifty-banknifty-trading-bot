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
                print(f"\n[SUCCESS] Selected {len(allocations)} strategies:")
                print(f"{'Strategy':<20} {'Weight':<10} {'Max Pos':<8} {'Priority':<8}")
                print("-" * 50)
                
                for allocation in allocations:
                    print(f"{allocation.strategy_name:<20} {allocation.allocation_weight:<10.1%} "
                          f"{allocation.max_positions:<8} {allocation.priority:<8}")
                
                # Generate adaptive signals
                print(f"\n[INFO] Generating adaptive signals...")
                signals = await selector.generate_adaptive_signals(scenario['data'])
                
                if signals:
                    print(f"[SUCCESS] Generated {len(signals)} total signals")
                    
                    print(f"\nTop 3 Signals:")
                    for i, signal in enumerate(signals[:3], 1):
                        print(f"  {i}. {signal.strategy_name}")
                        print(f"     Confidence: {signal.confidence_score:.1%}")
                        print(f"     Max Profit: Rs.{signal.max_profit}")
                        print(f"     Max Loss: Rs.{signal.max_loss}")
                        print(f"     Legs: {len(signal.legs)}")
                        print()
                else:
                    print("[WARNING] No signals generated despite strategy selection")
                    
            else:
                print("[WARNING] No strategies selected for this market scenario")
                
        except Exception as e:
            print(f"[ERROR] Error testing scenario: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("ADAPTIVE STRATEGY SELECTION TESTING COMPLETED")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(test_adaptive_strategy_selection())