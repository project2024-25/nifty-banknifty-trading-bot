#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.iron_condor import IronCondorStrategy
from src.strategies.base_strategy import MarketData


async def debug_iron_condor():
    print("DEBUG: Testing Iron Condor Signal Generation")
    
    iron_condor = IronCondorStrategy()
    
    # Debug NIFTY data
    nifty_data = MarketData(
        symbol="NIFTY",
        spot_price=24000.0,
        iv=35.0,  # Above 30% threshold
        volume=500000,  # Above 100k threshold
        oi=100000,
        last_updated=datetime.now()
    )
    
    print(f"Market data: {nifty_data.symbol}, IV: {nifty_data.iv}, Volume: {nifty_data.volume}")
    
    # Check if market is suitable
    is_suitable = iron_condor._is_market_suitable_for_iron_condor(nifty_data)
    print(f"Market suitable: {is_suitable}")
    
    # Check individual conditions
    is_market_open = iron_condor._is_market_suitable(nifty_data)
    print(f"Market open: {is_market_open}")
    print(f"IV check: {nifty_data.iv >= iron_condor.iv_percentile_min} (IV: {nifty_data.iv}, Min: {iron_condor.iv_percentile_min})")
    print(f"Volume check: {nifty_data.volume >= 100000} (Volume: {nifty_data.volume})")
    
    if is_suitable:
        # Try to create signal
        signal = await iron_condor._create_iron_condor_signal(nifty_data, "NIFTY")
        
        if signal:
            print(f"Signal created!")
            print(f"Confidence: {signal.confidence_score}")
            print(f"Min confidence: {iron_condor.min_confidence}")
            print(f"Legs: {len(signal.legs)}")
            print(f"Max profit: {signal.max_profit}")
            print(f"Max loss: {signal.max_loss}")
            
            # Calculate net premium
            net_premium = sum(
                leg.premium * (1 if leg.order_type.value == "SELL" else -1) 
                for leg in signal.legs
            )
            print(f"Net premium: {net_premium}")
            
            # Show legs
            for i, leg in enumerate(signal.legs):
                print(f"  Leg {i+1}: {leg.order_type.value} {leg.strike_price} {leg.option_type.value} @ {leg.premium}")
            
        else:
            print("No signal created - likely confidence score too low or minimum premium not met")
    
    # Try generating signals normally
    signals = await iron_condor.generate_signals(nifty_data)
    print(f"Signals generated: {len(signals)}")


if __name__ == "__main__":
    asyncio.run(debug_iron_condor())