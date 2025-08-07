#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.base_strategy import MarketData

# Import all strategies individually
from src.strategies.iron_condor import IronCondorStrategy
from src.strategies.conservative.bull_put_spread import BullPutSpreadStrategy
from src.strategies.conservative.bear_call_spread import BearCallSpreadStrategy
from src.strategies.conservative.bull_call_spread import BullCallSpreadStrategy
from src.strategies.conservative.bear_put_spread import BearPutSpreadStrategy
from src.strategies.conservative.butterfly_spread import ButterflySpreadStrategy
from src.strategies.conservative.covered_call import CoveredCallStrategy
from src.strategies.aggressive.long_straddle import LongStraddleStrategy
from src.strategies.aggressive.short_straddle import ShortStraddleStrategy
from src.strategies.aggressive.long_strangle import LongStrangleStrategy
from src.strategies.aggressive.short_strangle import ShortStrangleStrategy


async def test_individual_strategies():
    print("=" * 80)
    print("INDIVIDUAL STRATEGY TESTING")
    print("=" * 80)
    
    # Test market data
    market_data = MarketData(
        symbol="NIFTY",
        spot_price=24000.0,
        iv=35.0,  # Good IV for most strategies
        volume=500000,
        oi=100000,
        last_updated=datetime.now()
    )
    
    print(f"Test Market Data: {market_data.symbol}, Spot: {market_data.spot_price}, IV: {market_data.iv}%")
    
    # All strategies to test
    strategies = [
        ("Iron Condor", IronCondorStrategy()),
        ("Bull Put Spread", BullPutSpreadStrategy()),
        ("Bear Call Spread", BearCallSpreadStrategy()),
        ("Bull Call Spread", BullCallSpreadStrategy()),
        ("Bear Put Spread", BearPutSpreadStrategy()),
        ("Butterfly Spread", ButterflySpreadStrategy()),
        ("Covered Call", CoveredCallStrategy()),
        ("Long Straddle", LongStraddleStrategy()),
        ("Short Straddle", ShortStraddleStrategy()),
        ("Long Strangle", LongStrangleStrategy()),
        ("Short Strangle", ShortStrangleStrategy()),
    ]
    
    results = []
    
    for name, strategy in strategies:
        print(f"\n{'-'*60}")
        print(f"Testing: {name} ({strategy.strategy_type.value})")
        print(f"{'-'*60}")
        
        try:
            # Generate signals
            signals = await strategy.generate_signals(market_data)
            
            if signals:
                for i, signal in enumerate(signals, 1):
                    print(f"  [SIGNAL {i}] Generated!")
                    print(f"    Strategy: {signal.strategy_name}")
                    print(f"    Symbol: {signal.symbol}")
                    print(f"    Confidence: {signal.confidence_score:.1%}")
                    print(f"    Max Profit: Rs.{signal.max_profit}")
                    print(f"    Max Loss: Rs.{signal.max_loss}")
                    
                    if signal.max_loss != 0:
                        rr_ratio = abs(signal.max_profit / signal.max_loss)
                        print(f"    Risk-Reward: 1:{rr_ratio:.2f}")
                    
                    print(f"    Probability of Profit: {signal.probability_of_profit:.1%}")
                    print(f"    Legs: {len(signal.legs)}")
                    print(f"    Breakevens: {signal.breakeven_points}")
                    
                    # Show leg details
                    print(f"    Leg Details:")
                    for j, leg in enumerate(signal.legs, 1):
                        action = leg.order_type.value
                        option_type = leg.option_type.value
                        qty = f"x{leg.quantity}" if leg.quantity > 1 else ""
                        print(f"      {j}. {action} {leg.strike_price} {option_type} {qty} @ Rs.{leg.premium}")
                    
                    results.append({
                        'name': name,
                        'type': strategy.strategy_type.value,
                        'confidence': signal.confidence_score,
                        'max_profit': signal.max_profit,
                        'max_loss': abs(signal.max_loss),
                        'legs': len(signal.legs)
                    })
                    
            else:
                print(f"  [INFO] No signals generated")
                print(f"    Reason: Market conditions not suitable for {name}")
                
        except Exception as e:
            print(f"  [ERROR] Failed to test {name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*80}")
    print("INDIVIDUAL STRATEGY TEST SUMMARY")
    print(f"{'='*80}")
    
    if results:
        print(f"\nStrategies that generated signals: {len(results)}")
        print(f"\n{'Strategy':<18} {'Type':<12} {'Confidence':<12} {'R:R':<8} {'Legs':<6}")
        print("-" * 60)
        
        for result in results:
            rr_ratio = result['max_profit'] / result['max_loss'] if result['max_loss'] > 0 else 0
            print(f"{result['name']:<18} {result['type']:<12} {result['confidence']:<12.1%} {rr_ratio:<8.2f} {result['legs']:<6}")
    else:
        print("\nNo signals generated from any strategy")
    
    print(f"\n[SUCCESS] Individual strategy testing completed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_individual_strategies())