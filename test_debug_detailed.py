#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
import math
from src.strategies.iron_condor import IronCondorStrategy
from src.strategies.base_strategy import MarketData, OptionLeg, OptionType, OrderType


async def detailed_debug():
    print("DETAILED DEBUG: Iron Condor Signal Creation")
    
    iron_condor = IronCondorStrategy()
    
    # Test data
    nifty_data = MarketData(
        symbol="NIFTY",
        spot_price=24000.0,
        iv=35.0,
        volume=500000,
        oi=100000,
        last_updated=datetime.now()
    )
    
    # Manually create Iron Condor signal step by step
    spot_price = nifty_data.spot_price
    underlying = "NIFTY"
    
    print(f"Spot price: {spot_price}")
    
    # Strike calculation
    strike_interval = 50  # NIFTY
    atm_strike = round(spot_price / strike_interval) * strike_interval
    print(f"ATM strike: {atm_strike}")
    
    # Define strikes
    short_put_strike = atm_strike - (2 * strike_interval)
    long_put_strike = short_put_strike - iron_condor.wing_width
    short_call_strike = atm_strike + (2 * strike_interval) 
    long_call_strike = short_call_strike + iron_condor.wing_width
    
    print(f"Short Put: {short_put_strike}")
    print(f"Long Put: {long_put_strike}")
    print(f"Short Call: {short_call_strike}")
    print(f"Long Call: {long_call_strike}")
    
    # Calculate premiums
    short_put_premium = iron_condor._estimate_premium(short_put_strike, spot_price, OptionType.PUT, nifty_data.iv)
    long_put_premium = iron_condor._estimate_premium(long_put_strike, spot_price, OptionType.PUT, nifty_data.iv)
    short_call_premium = iron_condor._estimate_premium(short_call_strike, spot_price, OptionType.CALL, nifty_data.iv)
    long_call_premium = iron_condor._estimate_premium(long_call_strike, spot_price, OptionType.CALL, nifty_data.iv)
    
    print(f"Short Put Premium: {short_put_premium}")
    print(f"Long Put Premium: {long_put_premium}")
    print(f"Short Call Premium: {short_call_premium}")
    print(f"Long Call Premium: {long_call_premium}")
    
    # Net premium
    net_premium = short_put_premium - long_put_premium + short_call_premium - long_call_premium
    print(f"Net Premium: {net_premium}")
    print(f"Min Premium Required: {iron_condor.min_premium_collected}")
    print(f"Premium check passed: {net_premium >= iron_condor.min_premium_collected}")
    
    if net_premium >= iron_condor.min_premium_collected:
        # Calculate P&L
        max_profit = net_premium
        max_loss = iron_condor.wing_width - net_premium
        
        print(f"Max Profit: {max_profit}")
        print(f"Max Loss: {max_loss}")
        
        # Breakevens
        lower_breakeven = short_put_strike - net_premium
        upper_breakeven = short_call_strike + net_premium
        
        print(f"Lower Breakeven: {lower_breakeven}")
        print(f"Upper Breakeven: {upper_breakeven}")
        
        # Probability of profit
        profit_range = upper_breakeven - lower_breakeven
        total_range = long_call_strike - long_put_strike
        probability_of_profit = (profit_range / total_range) * 0.85
        
        print(f"Probability of Profit: {probability_of_profit:.2%}")
        
        # Confidence score calculation
        confidence_score = iron_condor._calculate_confidence_score(
            nifty_data, net_premium, probability_of_profit
        )
        
        print(f"Confidence Score: {confidence_score}")
        print(f"Min Confidence: {iron_condor.min_confidence}")
        print(f"Confidence check passed: {confidence_score >= iron_condor.min_confidence}")
        
    else:
        print("Premium check failed - signal would not be created")


if __name__ == "__main__":
    asyncio.run(detailed_debug())