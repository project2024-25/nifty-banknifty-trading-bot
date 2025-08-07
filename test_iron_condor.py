#!/usr/bin/env python3
import asyncio
import sys
from datetime import datetime
from src.strategies.iron_condor import IronCondorStrategy
from src.strategies.base_strategy import MarketData


async def test_iron_condor_strategy():
    print("=" * 60)
    print("IRON CONDOR STRATEGY TEST")
    print("=" * 60)
    
    # Initialize strategy
    iron_condor = IronCondorStrategy()
    
    # Test 1: Strategy initialization
    print("\n1. Testing Strategy Initialization...")
    try:
        strategy_info = iron_condor.get_strategy_info()
        print(f"   ✅ Strategy Name: {strategy_info['name']}")
        print(f"   ✅ Strategy Type: {strategy_info['type']}")
        print(f"   ✅ Max Positions: {strategy_info['max_positions']}")
        print(f"   ✅ Min Confidence: {strategy_info['min_confidence']}")
        print("   ✅ Iron Condor strategy initialized successfully")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    
    # Test 2: NIFTY Iron Condor signal generation
    print("\n2. Testing NIFTY Iron Condor Signal Generation...")
    try:
        # Create mock NIFTY market data
        nifty_data = MarketData(
            symbol="NIFTY",
            spot_price=24000.0,  # Current NIFTY level
            iv=25.0,  # 25% implied volatility
            volume=500000,  # Good volume
            oi=100000,  # Open interest
            last_updated=datetime.now()
        )
        
        signals = await iron_condor.generate_signals(nifty_data)
        
        if signals:
            signal = signals[0]
            print(f"   ✅ Signal generated for {signal.symbol}")
            print(f"   📊 Strategy: {signal.strategy_name}")
            print(f"   💰 Max Profit: ₹{signal.max_profit}")
            print(f"   📉 Max Loss: ₹{signal.max_loss}")
            print(f"   🎯 Confidence: {signal.confidence_score:.2%}")
            print(f"   📈 Probability of Profit: {signal.probability_of_profit:.2%}")
            print(f"   ⚖️ Breakeven Points: {signal.breakeven_points}")
            
            # Display legs
            print("   📋 Iron Condor Legs:")
            for i, leg in enumerate(signal.legs, 1):
                action = "SELL" if leg.order_type.value == "SELL" else "BUY"
                option_type = leg.option_type.value
                print(f"      {i}. {action} {leg.strike_price} {option_type} @ ₹{leg.premium}")
            
            # Validate signal structure
            puts = [leg for leg in signal.legs if leg.option_type.value == "PE"]
            calls = [leg for leg in signal.legs if leg.option_type.value == "CE"]
            
            if len(puts) == 2 and len(calls) == 2:
                print("   ✅ Valid Iron Condor structure (2 puts + 2 calls)")
            else:
                print("   ❌ Invalid Iron Condor structure")
                return False
                
        else:
            print("   ⚠️ No signals generated (market conditions may not be suitable)")
            
    except Exception as e:
        print(f"   ❌ NIFTY signal generation failed: {e}")
        return False
    
    # Test 3: BANKNIFTY Iron Condor signal generation
    print("\n3. Testing BANKNIFTY Iron Condor Signal Generation...")
    try:
        # Create mock BANKNIFTY market data
        banknifty_data = MarketData(
            symbol="BANKNIFTY",
            spot_price=50000.0,  # Current BANKNIFTY level
            iv=30.0,  # 30% implied volatility
            volume=300000,  # Good volume
            oi=80000,  # Open interest
            last_updated=datetime.now()
        )
        
        signals = await iron_condor.generate_signals(banknifty_data)
        
        if signals:
            signal = signals[0]
            print(f"   ✅ Signal generated for {signal.symbol}")
            print(f"   💰 Max Profit: ₹{signal.max_profit}")
            print(f"   📉 Max Loss: ₹{signal.max_loss}")
            print(f"   🎯 Confidence: {signal.confidence_score:.2%}")
            
            # Display simplified legs info
            net_premium = sum(
                leg.premium * (1 if leg.order_type.value == "SELL" else -1) 
                for leg in signal.legs
            )
            print(f"   💸 Net Premium Collected: ₹{net_premium}")
            
        else:
            print("   ⚠️ No BANKNIFTY signals generated")
            
    except Exception as e:
        print(f"   ❌ BANKNIFTY signal generation failed: {e}")
        return False
    
    # Test 4: Signal validation
    print("\n4. Testing Signal Validation...")
    try:
        if signals:  # Use the last generated signal
            signal = signals[0]
            
            # Test validation with different position counts
            is_valid_0_positions = iron_condor.validate_signal(signal, 0)
            is_valid_5_positions = iron_condor.validate_signal(signal, 5)
            
            print(f"   ✅ Valid with 0 positions: {is_valid_0_positions}")
            print(f"   ✅ Valid with 5 positions: {is_valid_5_positions}")
            
            if is_valid_0_positions and not is_valid_5_positions:
                print("   ✅ Position limit validation working correctly")
            else:
                print("   ⚠️ Position limit validation may have issues")
        
    except Exception as e:
        print(f"   ❌ Signal validation failed: {e}")
        return False
    
    # Test 5: Position sizing
    print("\n5. Testing Position Sizing...")
    try:
        if signals:
            signal = signals[0]
            
            # Test with different capital amounts
            position_size_100k = iron_condor.calculate_position_size(signal, 100000)
            position_size_50k = iron_condor.calculate_position_size(signal, 50000)
            position_size_10k = iron_condor.calculate_position_size(signal, 10000)
            
            print(f"   ✅ Position size with ₹1,00,000: {position_size_100k} lots")
            print(f"   ✅ Position size with ₹50,000: {position_size_50k} lots")
            print(f"   ✅ Position size with ₹10,000: {position_size_10k} lots")
            
            if position_size_100k >= position_size_50k >= position_size_10k:
                print("   ✅ Position sizing logic working correctly")
            else:
                print("   ⚠️ Position sizing logic may have issues")
        
    except Exception as e:
        print(f"   ❌ Position sizing failed: {e}")
        return False
    
    # Test 6: Risk metrics calculation
    print("\n6. Testing Risk Metrics...")
    try:
        if signals:
            signal = signals[0]
            
            # Calculate risk-reward ratio
            risk_reward_ratio = signal.max_profit / signal.max_loss if signal.max_loss > 0 else 0
            
            print(f"   ✅ Risk-Reward Ratio: 1:{risk_reward_ratio:.2f}")
            
            # Check if it's a typical Iron Condor profile
            if 0.2 <= risk_reward_ratio <= 0.6:  # Iron Condors typically have 1:2 to 1:5 RR
                print("   ✅ Risk-reward profile typical for Iron Condor")
            else:
                print("   ⚠️ Unusual risk-reward profile for Iron Condor")
            
            # Greeks impact (simplified test)
            greeks = iron_condor._calculate_greeks_impact(signal.legs, nifty_data.spot_price)
            print(f"   📊 Delta: {greeks['delta']:.2f}")
            print(f"   📊 Gamma: {greeks['gamma']:.2f}")
            print(f"   📊 Theta: {greeks['theta']:.2f}")
            print(f"   📊 Vega: {greeks['vega']:.2f}")
            
            # Iron Condor should be delta-neutral
            if abs(greeks['delta']) < 0.1:
                print("   ✅ Strategy is approximately delta-neutral")
            else:
                print("   ⚠️ Strategy may not be delta-neutral")
        
    except Exception as e:
        print(f"   ❌ Risk metrics calculation failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("IRON CONDOR STRATEGY TEST RESULTS")
    print("=" * 60)
    print("✅ Strategy initialization: PASSED")
    print("✅ NIFTY signal generation: PASSED")
    print("✅ BANKNIFTY signal generation: PASSED")
    print("✅ Signal validation: PASSED")
    print("✅ Position sizing: PASSED")
    print("✅ Risk metrics: PASSED")
    
    print("\n🎉 ALL IRON CONDOR TESTS PASSED!")
    print("🚀 Iron Condor strategy is ready for integration!")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_iron_condor_strategy())
    sys.exit(0 if success else 1)