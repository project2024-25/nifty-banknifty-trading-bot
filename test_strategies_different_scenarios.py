#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.base_strategy import MarketData

# Import strategies
from src.strategies.conservative.bull_put_spread import BullPutSpreadStrategy
from src.strategies.aggressive.long_straddle import LongStraddleStrategy
from src.strategies.aggressive.short_straddle import ShortStraddleStrategy
from src.strategies.conservative.butterfly_spread import ButterflySpreadStrategy


async def test_strategies_with_different_scenarios():
    print("=" * 80)
    print("TESTING STRATEGIES WITH VARIED CONDITIONS")  
    print("=" * 80)
    
    # Different market scenarios
    scenarios = [
        {
            "name": "High IV Market",
            "data": MarketData(
                symbol="NIFTY", spot_price=24000.0, iv=50.0,
                volume=600000, oi=100000, last_updated=datetime.now()
            )
        },
        {
            "name": "Low IV Market", 
            "data": MarketData(
                symbol="NIFTY", spot_price=24000.0, iv=15.0,
                volume=600000, oi=100000, last_updated=datetime.now()
            )
        },
        {
            "name": "Medium IV Market",
            "data": MarketData(
                symbol="NIFTY", spot_price=24000.0, iv=30.0,
                volume=600000, oi=100000, last_updated=datetime.now()
            )
        }
    ]
    
    strategies_to_test = [
        ("Bull Put Spread", BullPutSpreadStrategy()),
        ("Long Straddle", LongStraddleStrategy()),  
        ("Short Straddle", ShortStraddleStrategy()),
        ("Butterfly Spread", ButterflySpreadStrategy()),
    ]
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"IV: {scenario['data'].iv}%, Spot: {scenario['data'].spot_price}")
        print(f"{'='*60}")
        
        for name, strategy in strategies_to_test:
            print(f"\n  Testing {name}...")
            
            try:
                signals = await strategy.generate_signals(scenario['data'])
                
                if signals:
                    signal = signals[0]
                    print(f"    [SUCCESS] Signal generated!")
                    print(f"    Confidence: {signal.confidence_score:.1%}")
                    print(f"    Max Profit: Rs.{signal.max_profit:.2f}")
                    print(f"    Max Loss: Rs.{abs(signal.max_loss):.2f}")
                    rr = signal.max_profit / abs(signal.max_loss) if signal.max_loss != 0 else 0
                    print(f"    Risk-Reward: 1:{rr:.2f}")
                else:
                    print(f"    [INFO] No signal generated")
                    
            except Exception as e:
                print(f"    [ERROR] {e}")
    
    print(f"\n{'='*80}")
    print("SCENARIO TESTING COMPLETED")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(test_strategies_with_different_scenarios())