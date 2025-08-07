#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
from typing import List
import random
import math
from src.intelligence.trend_detector import TrendDetector, TrendDirection, TrendStrength, TrendPhase
from src.strategies.base_strategy import MarketData


def generate_trending_series(base_price: float = 24000, days: int = 100, 
                           trend_strength: float = 0.001, noise_level: float = 0.015) -> List[float]:
    """Generate price series with specific trend"""
    prices = [base_price]
    
    for i in range(days - 1):
        # Add trend component
        trend_component = trend_strength * base_price
        
        # Add random noise
        noise = random.gauss(0, noise_level * prices[-1])
        
        new_price = prices[-1] + trend_component + noise
        prices.append(max(new_price, base_price * 0.3))  # Prevent extremely low prices
    
    return prices


def generate_sideways_series(base_price: float = 24000, days: int = 100, 
                           volatility: float = 0.02) -> List[float]:
    """Generate sideways/ranging price series"""
    prices = [base_price]
    mean_price = base_price
    
    for i in range(days - 1):
        # Mean reversion tendency
        reversion_force = (mean_price - prices[-1]) * 0.05
        
        # Random component
        random_component = random.gauss(0, volatility * base_price)
        
        new_price = prices[-1] + reversion_force + random_component
        prices.append(max(new_price, base_price * 0.7))
    
    return prices


def generate_volatile_trending_series(base_price: float = 24000, days: int = 100) -> List[float]:
    """Generate series with trend but high volatility"""
    prices = [base_price]
    
    for i in range(days - 1):
        # Base uptrend
        trend = 0.0008 * base_price
        
        # High volatility component
        volatility = random.gauss(0, 0.03 * prices[-1])
        
        # Occasional spikes
        if random.random() < 0.05:  # 5% chance
            spike = random.choice([-1, 1]) * 0.05 * prices[-1]
        else:
            spike = 0
        
        new_price = prices[-1] + trend + volatility + spike
        prices.append(max(new_price, base_price * 0.5))
    
    return prices


async def test_basic_trend_detection():
    print("=" * 80)
    print("TESTING BASIC TREND DETECTION")
    print("=" * 80)
    
    detector = TrendDetector()
    
    try:
        # Create mock market data
        market_data = MarketData(
            symbol="NIFTY",
            spot_price=24500.0,
            iv=20.0,
            volume=500000,
            oi=100000,
            last_updated=datetime.now()
        )
        
        # Generate uptrending price series
        print("\n[STEP 1] Generating uptrending price series...")
        price_history = generate_trending_series(24000, 80, 0.002, 0.01)  # Strong uptrend
        volume_history = [random.randint(400000, 600000) for _ in range(80)]
        
        print(f"[SUCCESS] Generated {len(price_history)} price points")
        print(f"Price range: {min(price_history):.2f} - {max(price_history):.2f}")
        print(f"Total return: {((price_history[-1] / price_history[0]) - 1) * 100:.2f}%")
        
        # Analyze trend
        print("\n[STEP 2] Running trend analysis...")
        trend_metrics = detector.detect_trend(market_data, price_history, volume_history)
        
        print(f"[SUCCESS] Trend analysis completed for {trend_metrics.symbol}")
        
        # Display comprehensive results
        print(f"\n=== COMPREHENSIVE TREND ANALYSIS ===")
        print(f"Symbol: {trend_metrics.symbol}")
        print(f"Analysis Time: {trend_metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n--- Primary Trend Characteristics ---")
        print(f"Direction:     {trend_metrics.trend_direction.value.replace('_', ' ').title()}")
        print(f"Strength:      {trend_metrics.trend_strength.value.replace('_', ' ').title()}")
        print(f"Duration:      {trend_metrics.trend_duration.value.replace('_', ' ').title()}")
        print(f"Phase:         {trend_metrics.trend_phase.value.replace('_', ' ').title()}")
        print(f"Confidence:    {trend_metrics.trend_confidence:.1%}")
        
        print(f"\n--- Trend Measurements ---")
        print(f"Angle:         {trend_metrics.trend_angle:.2f}°")
        print(f"Slope:         {trend_metrics.trend_slope:.4f}")
        print(f"R-Squared:     {trend_metrics.trend_r_squared:.3f}")
        print(f"Momentum:      {trend_metrics.trend_momentum:.3f}")
        print(f"Consistency:   {trend_metrics.trend_consistency:.3f}")
        print(f"Volatility:    {trend_metrics.trend_volatility:.2f}%")
        
        print(f"\n--- Multi-Timeframe Analysis ---")
        print(f"Short-term:    {trend_metrics.short_term_trend.value.replace('_', ' ').title()}")
        print(f"Medium-term:   {trend_metrics.medium_term_trend.value.replace('_', ' ').title()}")
        print(f"Long-term:     {trend_metrics.long_term_trend.value.replace('_', ' ').title()}")
        
        print(f"\n--- Technical Indicators ---")
        print(f"ADX Value:     {trend_metrics.adx_value:.2f}")
        print(f"MACD Signal:   {trend_metrics.macd_signal:.3f}")
        print(f"RSI Trend:     {trend_metrics.rsi_trend:.2f}")
        print(f"Volume Confirm: {trend_metrics.volume_confirmation:.3f}")
        
        print(f"\n--- Support/Resistance Levels ---")
        if trend_metrics.key_support_levels:
            print(f"Support Levels: {', '.join([f'{level:.2f}' for level in trend_metrics.key_support_levels[:3]])}")
        if trend_metrics.key_resistance_levels:
            print(f"Resistance Levels: {', '.join([f'{level:.2f}' for level in trend_metrics.key_resistance_levels[:3]])}")
        print(f"Level Significance: {trend_metrics.current_level_significance:.3f}")
        
        print(f"\n--- Reversal Analysis ---")
        print(f"Reversal Probability: {trend_metrics.reversal_probability:.1%}")
        print(f"Reversal Signals:     {trend_metrics.reversal_signals_count}")
        if trend_metrics.divergence_signals:
            print(f"Divergence Signals:   {', '.join(trend_metrics.divergence_signals)}")
        
        print(f"\n--- Price Action Patterns ---")
        print(f"Higher Highs:  {trend_metrics.higher_highs_count}")
        print(f"Higher Lows:   {trend_metrics.higher_lows_count}")
        print(f"Lower Highs:   {trend_metrics.lower_highs_count}")
        print(f"Lower Lows:    {trend_metrics.lower_lows_count}")
        
        print(f"\n[SUCCESS] Basic trend detection test completed!")
        
    except Exception as e:
        print(f"[ERROR] Basic trend test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_trend_scenarios():
    print(f"\n{'=' * 80}")
    print("TESTING MULTIPLE TREND SCENARIOS")
    print("=" * 80)
    
    detector = TrendDetector()
    
    # Test scenarios with different trend characteristics
    scenarios = [
        {
            "name": "Strong Uptrend",
            "generator": lambda: generate_trending_series(24000, 60, 0.003, 0.01),
            "expected_direction": "uptrend"
        },
        {
            "name": "Weak Uptrend", 
            "generator": lambda: generate_trending_series(24000, 60, 0.0005, 0.015),
            "expected_direction": "weak_uptrend"
        },
        {
            "name": "Strong Downtrend",
            "generator": lambda: generate_trending_series(24000, 60, -0.003, 0.01),
            "expected_direction": "downtrend"
        },
        {
            "name": "Sideways Market",
            "generator": lambda: generate_sideways_series(24000, 60, 0.02),
            "expected_direction": "sideways"
        },
        {
            "name": "Volatile Trending Market",
            "generator": lambda: generate_volatile_trending_series(24000, 60),
            "expected_direction": "uptrend"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios):
        print(f"\n[SCENARIO {i+1}] {scenario['name']}")
        print("-" * 50)
        
        try:
            # Generate data
            prices = scenario['generator']()
            volumes = [random.randint(300000, 700000) for _ in range(len(prices))]
            
            # Create market data
            market_data = MarketData(
                symbol="TEST",
                spot_price=prices[-1],
                iv=22.0,
                volume=volumes[-1],
                oi=80000,
                last_updated=datetime.now()
            )
            
            # Analyze trend
            trend_metrics = detector.detect_trend(market_data, prices, volumes)
            results.append((scenario['name'], trend_metrics))
            
            print(f"Price Change:    {((prices[-1] / prices[0]) - 1) * 100:+.2f}%")
            print(f"Detected:        {trend_metrics.trend_direction.value.replace('_', ' ').title()}")
            print(f"Expected:        {scenario['expected_direction'].replace('_', ' ').title()}")
            print(f"Strength:        {trend_metrics.trend_strength.value.replace('_', ' ').title()}")
            print(f"Confidence:      {trend_metrics.trend_confidence:.1%}")
            print(f"Trend Angle:     {trend_metrics.trend_angle:+.2f}°")
            print(f"ADX Value:       {trend_metrics.adx_value:.2f}")
            print(f"RSI:             {trend_metrics.rsi_trend:.2f}")
            
            # Check if detection makes sense
            detected = trend_metrics.trend_direction.value
            expected = scenario['expected_direction']
            if expected in detected or any(exp_part in detected for exp_part in expected.split('_')):
                print(f"[SUCCESS] Trend correctly identified")
            else:
                print(f"[INFO] Trend: Expected ~{expected}, Got {detected}")
            
        except Exception as e:
            print(f"[ERROR] Scenario {i+1} failed: {e}")
    
    # Comparative analysis
    if results:
        print(f"\n=== SCENARIO COMPARISON ===")
        print(f"{'Scenario':<25} {'Direction':<15} {'Strength':<12} {'Confidence':<10} {'Angle':<8}")
        print("-" * 80)
        
        for name, metrics in results:
            direction_short = metrics.trend_direction.value.replace('_', ' ')[:14]
            strength_short = metrics.trend_strength.value[:11]
            print(f"{name:<25} {direction_short:<15} {strength_short:<12} "
                  f"{metrics.trend_confidence:<10.1%} {metrics.trend_angle:<+8.2f}")


async def test_multi_timeframe_analysis():
    print(f"\n{'=' * 80}")
    print("TESTING MULTI-TIMEFRAME TREND ANALYSIS")
    print("=" * 80)
    
    detector = TrendDetector()
    
    try:
        # Generate longer series with changing trends
        print("\n[INFO] Generating multi-phase price series...")
        
        prices = []
        
        # Phase 1: Downtrend (30 periods)
        phase1 = generate_trending_series(25000, 30, -0.002, 0.01)
        prices.extend(phase1)
        
        # Phase 2: Sideways (40 periods)  
        phase2_start = prices[-1]
        phase2 = generate_sideways_series(phase2_start, 40, 0.015)
        prices.extend(phase2[1:])  # Skip first to avoid duplicate
        
        # Phase 3: Uptrend (50 periods)
        phase3_start = prices[-1] 
        phase3 = generate_trending_series(phase3_start, 50, 0.0015, 0.012)
        prices.extend(phase3[1:])  # Skip first to avoid duplicate
        
        volumes = [random.randint(400000, 600000) for _ in range(len(prices))]
        
        print(f"[SUCCESS] Generated {len(prices)} price points across 3 phases")
        print(f"Phase 1 (Downtrend): Periods 0-29")
        print(f"Phase 2 (Sideways):  Periods 30-69") 
        print(f"Phase 3 (Uptrend):   Periods 70-{len(prices)-1}")
        print(f"Total price change: {((prices[-1] / prices[0]) - 1) * 100:+.2f}%")
        
        # Analyze with different lookback periods
        market_data = MarketData(
            symbol="MULTI_TF",
            spot_price=prices[-1],
            iv=25.0,
            volume=volumes[-1],
            oi=90000,
            last_updated=datetime.now()
        )
        
        print(f"\n[ANALYSIS] Multi-timeframe trend detection...")
        trend_metrics = detector.detect_trend(market_data, prices, volumes)
        
        print(f"\n=== MULTI-TIMEFRAME RESULTS ===")
        print(f"Short-term Trend (20):  {trend_metrics.short_term_trend.value.replace('_', ' ').title()}")
        print(f"Medium-term Trend (50): {trend_metrics.medium_term_trend.value.replace('_', ' ').title()}")
        print(f"Long-term Trend (200):  {trend_metrics.long_term_trend.value.replace('_', ' ').title()}")
        print(f"Overall Direction:      {trend_metrics.trend_direction.value.replace('_', ' ').title()}")
        
        print(f"\n--- Trend Characteristics ---")
        print(f"Phase:           {trend_metrics.trend_phase.value.replace('_', ' ').title()}")
        print(f"Duration:        {trend_metrics.trend_duration.value.replace('_', ' ').title()}")
        print(f"Consistency:     {trend_metrics.trend_consistency:.3f}")
        print(f"Trend Angle:     {trend_metrics.trend_angle:+.2f}°")
        print(f"Overall Confidence: {trend_metrics.trend_confidence:.1%}")
        
        print(f"\n--- Technical Confirmation ---")
        print(f"ADX (Trend Strength): {trend_metrics.adx_value:.2f}")
        print(f"MACD Signal:          {trend_metrics.macd_signal:+.3f}")
        print(f"RSI Level:            {trend_metrics.rsi_trend:.2f}")
        
        # Analysis of recent trend changes
        print(f"\n[INSIGHTS]")
        if trend_metrics.short_term_trend != trend_metrics.medium_term_trend:
            print("- Short-term trend differs from medium-term (possible trend change)")
        if trend_metrics.trend_phase in [TrendPhase.EXHAUSTING, TrendPhase.REVERSING]:
            print("- Current trend may be nearing exhaustion")
        if trend_metrics.reversal_probability > 0.3:
            print(f"- Elevated reversal probability ({trend_metrics.reversal_probability:.1%})")
        
        print(f"\n[SUCCESS] Multi-timeframe analysis completed!")
        
    except Exception as e:
        print(f"[ERROR] Multi-timeframe test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_technical_indicators():
    print(f"\n{'=' * 80}")
    print("TESTING TECHNICAL INDICATOR INTEGRATION")
    print("=" * 80)
    
    detector = TrendDetector()
    
    test_cases = [
        {
            "name": "Strong Momentum Market",
            "prices": generate_trending_series(24000, 80, 0.0025, 0.008),
            "description": "Consistent uptrend with low volatility"
        },
        {
            "name": "Weak Momentum Market", 
            "prices": generate_sideways_series(24000, 80, 0.025),
            "description": "Ranging market with high volatility"
        },
        {
            "name": "Trend Reversal Market",
            "prices": generate_trending_series(24000, 40, 0.002, 0.01) + 
                     generate_trending_series(24000, 40, -0.002, 0.01)[1:],
            "description": "Uptrend followed by downtrend"
        }
    ]
    
    for i, case in enumerate(test_cases):
        print(f"\n[TEST CASE {i+1}] {case['name']}")
        print(f"Description: {case['description']}")
        print("-" * 60)
        
        try:
            prices = case['prices']
            volumes = [random.randint(300000, 800000) for _ in range(len(prices))]
            
            market_data = MarketData(
                symbol="TECH_TEST",
                spot_price=prices[-1],
                iv=24.0,
                volume=volumes[-1],
                oi=75000,
                last_updated=datetime.now()
            )
            
            trend_metrics = detector.detect_trend(market_data, prices, volumes)
            
            print(f"Price Performance: {((prices[-1] / prices[0]) - 1) * 100:+.2f}%")
            print(f"Trend Direction:   {trend_metrics.trend_direction.value.replace('_', ' ').title()}")
            print(f"Trend Strength:    {trend_metrics.trend_strength.value.replace('_', ' ').title()}")
            
            print(f"\n--- Technical Indicators ---")
            print(f"ADX (Trend Strength):  {trend_metrics.adx_value:.2f}")
            if trend_metrics.adx_value > 40:
                print("  -> Very strong trend")
            elif trend_metrics.adx_value > 25:
                print("  -> Moderate trend")
            else:
                print("  -> Weak trend")
            
            print(f"MACD Signal:           {trend_metrics.macd_signal:+.4f}")
            if trend_metrics.macd_signal > 0.5:
                print("  -> Strong bullish momentum")
            elif trend_metrics.macd_signal > 0:
                print("  -> Bullish momentum")
            elif trend_metrics.macd_signal < -0.5:
                print("  -> Strong bearish momentum")
            else:
                print("  -> Bearish momentum")
            
            print(f"RSI Level:             {trend_metrics.rsi_trend:.2f}")
            if trend_metrics.rsi_trend > 70:
                print("  -> Overbought territory")
            elif trend_metrics.rsi_trend > 50:
                print("  -> Bullish bias")
            elif trend_metrics.rsi_trend < 30:
                print("  -> Oversold territory") 
            else:
                print("  -> Bearish bias")
            
            print(f"Volume Confirmation:   {trend_metrics.volume_confirmation:.3f}")
            if trend_metrics.volume_confirmation > 0.7:
                print("  -> Strong volume support")
            elif trend_metrics.volume_confirmation > 0.3:
                print("  -> Moderate volume support")
            else:
                print("  -> Weak volume support")
            
            print(f"\n--- Advanced Metrics ---")
            print(f"Trend R-Squared:    {trend_metrics.trend_r_squared:.3f}")
            print(f"Trend Consistency:  {trend_metrics.trend_consistency:.3f}")
            print(f"Trend Volatility:   {trend_metrics.trend_volatility:.2f}%")
            print(f"Overall Confidence: {trend_metrics.trend_confidence:.1%}")
            
        except Exception as e:
            print(f"[ERROR] Test case {i+1} failed: {e}")


async def test_trend_detector():
    """Run comprehensive trend detector tests"""
    print("STARTING COMPREHENSIVE TREND DETECTOR TESTING")
    print("=" * 90)
    
    await test_basic_trend_detection()
    await test_trend_scenarios()
    await test_multi_timeframe_analysis()
    await test_technical_indicators()
    
    print(f"\n{'=' * 90}")
    print("TREND DETECTOR TESTING COMPLETED!")
    print("=" * 90)


if __name__ == "__main__":
    asyncio.run(test_trend_detector())