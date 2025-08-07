#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.conservative.bull_put_spread import BullPutSpreadStrategy
from src.strategies.base_strategy import MarketData


async def debug_bull_put_spread():
    print("DEBUGGING BULL PUT SPREAD STRATEGY")
    print("=" * 50)
    
    strategy = BullPutSpreadStrategy()
    
    market_data = MarketData(
        symbol="NIFTY",
        spot_price=24000.0,
        iv=30.0,
        volume=500000,
        oi=100000,
        last_updated=datetime.now()
    )
    
    print(f"Market Data: Spot {market_data.spot_price}, IV {market_data.iv}%")
    
    # Check market suitability
    is_suitable = strategy._is_market_suitable_for_bull_put_spread(market_data)
    print(f"Market suitable: {is_suitable}")
    print(f"IV check: {market_data.iv >= strategy.min_iv_percentile} (IV: {market_data.iv}, Min: {strategy.min_iv_percentile})")
    print(f"Volume check: {market_data.volume >= 100000} (Volume: {market_data.volume})")
    
    if is_suitable:
        signal = await strategy._create_bull_put_spread_signal(market_data)
        
        if signal:
            print(f"Signal created!")
            print(f"Confidence: {signal.confidence_score}")
            print(f"Min confidence: {strategy.min_confidence}")
            
        else:
            print("Signal creation failed - likely confidence too low or premium too low")
            
            # Debug the signal creation
            spot_price = market_data.spot_price
            strike_interval = 50  # NIFTY
            atm_strike = round(spot_price / strike_interval) * strike_interval
            min_otm_distance = max(2 * strike_interval, spot_price * strategy.min_moneyness)
            short_put_strike = atm_strike - min_otm_distance
            long_put_strike = short_put_strike - strategy.spread_width
            
            print(f"Debug calculations:")
            print(f"  ATM Strike: {atm_strike}")
            print(f"  Short Put Strike: {short_put_strike}")
            print(f"  Long Put Strike: {long_put_strike}")
            print(f"  Min OTM distance: {min_otm_distance}")
            
            # Calculate premiums
            from src.strategies.base_strategy import OptionType
            short_premium = strategy._estimate_premium(short_put_strike, spot_price, OptionType.PUT, market_data.iv)
            long_premium = strategy._estimate_premium(long_put_strike, spot_price, OptionType.PUT, market_data.iv)
            net_premium = short_premium - long_premium
            
            print(f"  Short Put Premium: {short_premium}")
            print(f"  Long Put Premium: {long_premium}")
            print(f"  Net Premium: {net_premium}")
            print(f"  Min Premium Required: {strategy.min_premium_collected}")
            
            if net_premium >= strategy.min_premium_collected:
                print("  Premium check passed!")
                
                # Check confidence
                max_profit = net_premium
                max_loss = strategy.spread_width - net_premium
                breakeven = short_put_strike - net_premium
                distance_to_breakeven = spot_price - breakeven
                prob_profit = min(0.85, distance_to_breakeven / (spot_price * 0.1))
                
                confidence = strategy._calculate_confidence_score(market_data, net_premium, prob_profit, distance_to_breakeven)
                print(f"  Confidence score: {confidence}")
                print(f"  Min required: {strategy.min_confidence}")
                
            else:
                print("  Premium check failed!")
    
    else:
        print("Market not suitable")


if __name__ == "__main__":
    asyncio.run(debug_bull_put_spread())