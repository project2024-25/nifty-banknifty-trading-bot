#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
from typing import List
import random
import math
from src.intelligence.volatility_analyzer import VolatilityAnalyzer, VolatilityRegime, VolatilityTrend
from src.strategies.base_strategy import MarketData


def generate_mock_price_series(base_price: float = 24000, days: int = 100, volatility: float = 0.02) -> List[float]:
    """Generate realistic mock price series with controlled volatility"""
    prices = [base_price]
    
    for i in range(days - 1):
        # Generate random return with specified volatility
        daily_return = random.gauss(0, volatility)  # Mean 0, std = volatility
        new_price = prices[-1] * (1 + daily_return)
        prices.append(max(new_price, base_price * 0.5))  # Prevent negative prices
    
    return prices


def create_volatile_series(base_price: float = 24000, days: int = 100) -> List[float]:
    """Create series with increasing volatility towards end"""
    prices = [base_price]
    
    for i in range(days - 1):
        # Volatility increases over time
        vol_factor = 1 + (i / days) * 2  # Volatility doubles by end
        daily_vol = 0.015 * vol_factor
        
        daily_return = random.gauss(0, daily_vol)
        new_price = prices[-1] * (1 + daily_return)
        prices.append(max(new_price, base_price * 0.3))
    
    return prices


async def test_basic_volatility_analysis():
    print("=" * 80)
    print("TESTING BASIC VOLATILITY ANALYSIS")
    print("=" * 80)
    
    analyzer = VolatilityAnalyzer()
    
    try:
        # Create mock market data
        market_data = MarketData(
            symbol="NIFTY",
            spot_price=24000.0,
            iv=22.5,
            volume=500000,
            oi=100000,
            last_updated=datetime.now()
        )
        
        # Generate price history
        print("\n[STEP 1] Generating mock price series...")
        price_history = generate_mock_price_series(24000, 90, 0.02)  # 90 days, 2% daily vol
        
        print(f"[SUCCESS] Generated {len(price_history)} price points")
        print(f"Price range: {min(price_history):.2f} - {max(price_history):.2f}")
        
        # Analyze volatility
        print("\n[STEP 2] Running volatility analysis...")
        vol_metrics = analyzer.analyze_volatility(market_data, price_history)
        
        print(f"[SUCCESS] Volatility analysis completed for {vol_metrics.symbol}")
        
        # Display results
        print(f"\n=== VOLATILITY ANALYSIS RESULTS ===")
        print(f"Symbol: {vol_metrics.symbol}")
        print(f"Analysis Time: {vol_metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n--- Realized Volatility ---")
        print(f"Daily (10-day):    {vol_metrics.realized_vol_daily:.2f}%")
        print(f"Weekly (30-day):   {vol_metrics.realized_vol_weekly:.2f}%")
        print(f"Monthly (90-day):  {vol_metrics.realized_vol_monthly:.2f}%")
        print(f"Implied Vol:       {vol_metrics.implied_vol_current:.2f}%")
        
        print(f"\n--- Historical Context ---")
        print(f"30-day Percentile: {vol_metrics.vol_percentile_30d:.1%}")
        print(f"90-day Percentile: {vol_metrics.vol_percentile_90d:.1%}")
        print(f"1-year Percentile: {vol_metrics.vol_percentile_1y:.1%}")
        
        print(f"\n--- Volatility Regime ---")
        print(f"Current Regime:    {vol_metrics.current_regime.value.replace('_', ' ').title()}")
        print(f"Regime Confidence: {vol_metrics.regime_confidence:.1%}")
        print(f"Regime Stability:  {vol_metrics.regime_stability:.1%}")
        
        print(f"\n--- Volatility Forecasting ---")
        print(f"Predicted 1-day:   {vol_metrics.predicted_vol_1d:.2f}%")
        print(f"Predicted 5-day:   {vol_metrics.predicted_vol_5d:.2f}%")
        print(f"Predicted 30-day:  {vol_metrics.predicted_vol_30d:.2f}%")
        print(f"Forecast Confidence: {vol_metrics.vol_forecast_confidence:.1%}")
        
        print(f"\n--- Volatility Dynamics ---")
        print(f"Vol Trend:         {vol_metrics.vol_trend.value.replace('_', ' ').title()}")
        print(f"Vol Acceleration:  {vol_metrics.vol_acceleration:.4f}")
        print(f"Mean Reversion:    {vol_metrics.vol_mean_reversion_speed:.4f}")
        
        print(f"\n--- Risk Metrics ---")
        print(f"Vol Risk Premium:  {vol_metrics.vol_risk_premium:.2f}%")
        print(f"Uncertainty Index: {vol_metrics.vol_uncertainty_index:.3f}")
        print(f"Tail Risk:         {vol_metrics.tail_risk_indicator:.3f}")
        
        if vol_metrics.vol_term_structure:
            print(f"\n--- Term Structure ---")
            for period, vol in vol_metrics.vol_term_structure.items():
                print(f"{period}: {vol:.2f}%")
        
        print(f"\n[SUCCESS] Basic volatility analysis test completed!")
        
    except Exception as e:
        print(f"[ERROR] Basic volatility test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_volatility_regimes():
    print(f"\n{'=' * 80}")
    print("TESTING VOLATILITY REGIME CLASSIFICATION")
    print("=" * 80)
    
    analyzer = VolatilityAnalyzer()
    
    # Test different volatility scenarios
    scenarios = [
        {
            "name": "Low Volatility Market", 
            "base_vol": 0.008,  # 0.8% daily
            "expected_regime": "low"
        },
        {
            "name": "Normal Volatility Market",
            "base_vol": 0.015,  # 1.5% daily
            "expected_regime": "normal"
        },
        {
            "name": "High Volatility Market",
            "base_vol": 0.035,  # 3.5% daily
            "expected_regime": "high"
        },
        {
            "name": "Extreme Volatility Market",
            "base_vol": 0.055,  # 5.5% daily
            "expected_regime": "extreme"
        }
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n[SCENARIO {i+1}] {scenario['name']}")
        print("-" * 50)
        
        try:
            # Generate price series with specific volatility
            prices = generate_mock_price_series(24000, 60, scenario['base_vol'])
            
            # Create market data
            market_data = MarketData(
                symbol="TEST",
                spot_price=prices[-1],
                iv=25.0,
                volume=100000,
                oi=50000,
                last_updated=datetime.now()
            )
            
            # Analyze volatility
            vol_metrics = analyzer.analyze_volatility(market_data, prices)
            
            print(f"Price Volatility: {scenario['base_vol']*100:.1f}% daily target")
            print(f"Realized Vol:     {vol_metrics.realized_vol_daily:.2f}%")
            print(f"Detected Regime:  {vol_metrics.current_regime.value.replace('_', ' ').title()}")
            print(f"Confidence:       {vol_metrics.regime_confidence:.1%}")
            print(f"Vol Percentile:   {vol_metrics.vol_percentile_90d:.1%}")
            
            # Check if regime detection makes sense
            detected = vol_metrics.current_regime.value
            if scenario['expected_regime'] in detected or detected in scenario['expected_regime']:
                print(f"[SUCCESS] Regime correctly classified")
            else:
                print(f"[INFO] Regime: Expected ~{scenario['expected_regime']}, Got {detected}")
        
        except Exception as e:
            print(f"[ERROR] Scenario {i+1} failed: {e}")


async def test_volatility_forecasting():
    print(f"\n{'=' * 80}")
    print("TESTING VOLATILITY FORECASTING")
    print("=" * 80)
    
    analyzer = VolatilityAnalyzer()
    
    try:
        # Test with stable volatility series
        print("\n[TEST 1] Stable Volatility Series")
        print("-" * 40)
        
        stable_prices = generate_mock_price_series(24000, 100, 0.018)
        
        market_data = MarketData(
            symbol="STABLE",
            spot_price=stable_prices[-1],
            iv=20.0,
            volume=200000,
            oi=75000,
            last_updated=datetime.now()
        )
        
        vol_metrics = analyzer.analyze_volatility(market_data, stable_prices)
        
        print(f"Current Realized Vol:  {vol_metrics.realized_vol_daily:.2f}%")
        print(f"1-day Forecast:        {vol_metrics.predicted_vol_1d:.2f}%")
        print(f"5-day Forecast:        {vol_metrics.predicted_vol_5d:.2f}%")
        print(f"30-day Forecast:       {vol_metrics.predicted_vol_30d:.2f}%")
        print(f"Forecast Confidence:   {vol_metrics.vol_forecast_confidence:.1%}")
        print(f"Vol Trend:             {vol_metrics.vol_trend.value}")
        
        # Test with increasing volatility series
        print("\n[TEST 2] Increasing Volatility Series")
        print("-" * 40)
        
        volatile_prices = create_volatile_series(24000, 100)
        
        market_data.symbol = "VOLATILE"
        market_data.spot_price = volatile_prices[-1]
        
        vol_metrics = analyzer.analyze_volatility(market_data, volatile_prices)
        
        print(f"Current Realized Vol:  {vol_metrics.realized_vol_daily:.2f}%")
        print(f"1-day Forecast:        {vol_metrics.predicted_vol_1d:.2f}%")
        print(f"5-day Forecast:        {vol_metrics.predicted_vol_5d:.2f}%")
        print(f"30-day Forecast:       {vol_metrics.predicted_vol_30d:.2f}%")
        print(f"Forecast Confidence:   {vol_metrics.vol_forecast_confidence:.1%}")
        print(f"Vol Trend:             {vol_metrics.vol_trend.value}")
        
        # Compare forecasts
        print(f"\n[ANALYSIS] Forecasting Comparison")
        print(f"Stable vs Volatile 1-day forecast difference: {abs(vol_metrics.predicted_vol_1d - vol_metrics.predicted_vol_1d):.2f}%")
        
        print(f"\n[SUCCESS] Volatility forecasting tests completed!")
        
    except Exception as e:
        print(f"[ERROR] Volatility forecasting test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_multiple_symbols():
    print(f"\n{'=' * 80}")
    print("TESTING MULTI-SYMBOL VOLATILITY ANALYSIS")
    print("=" * 80)
    
    analyzer = VolatilityAnalyzer()
    
    symbols_data = [
        {"symbol": "NIFTY", "base_price": 24000, "vol": 0.015, "iv": 18.5},
        {"symbol": "BANKNIFTY", "base_price": 50000, "vol": 0.025, "iv": 22.0},
        {"symbol": "RELIANCE", "base_price": 2800, "vol": 0.020, "iv": 28.0},
        {"symbol": "TCS", "base_price": 3400, "vol": 0.018, "iv": 25.5}
    ]
    
    results = {}
    
    for data in symbols_data:
        try:
            print(f"\n[PROCESSING] {data['symbol']}")
            print(f"Base Price: {data['base_price']}, Target Vol: {data['vol']*100:.1f}%")
            
            # Generate price series
            prices = generate_mock_price_series(data['base_price'], 80, data['vol'])
            
            # Create market data
            market_data = MarketData(
                symbol=data['symbol'],
                spot_price=prices[-1],
                iv=data['iv'],
                volume=random.randint(100000, 500000),
                oi=random.randint(50000, 200000),
                last_updated=datetime.now()
            )
            
            # Analyze
            vol_metrics = analyzer.analyze_volatility(market_data, prices)
            results[data['symbol']] = vol_metrics
            
            print(f"  Realized Vol:    {vol_metrics.realized_vol_daily:.2f}%")
            print(f"  Implied Vol:     {vol_metrics.implied_vol_current:.2f}%")
            print(f"  Vol Premium:     {vol_metrics.vol_risk_premium:.2f}%")
            print(f"  Regime:          {vol_metrics.current_regime.value.replace('_', ' ').title()}")
            print(f"  Confidence:      {vol_metrics.regime_confidence:.1%}")
            
        except Exception as e:
            print(f"[ERROR] Analysis failed for {data['symbol']}: {e}")
    
    # Summary comparison
    if results:
        print(f"\n=== MULTI-SYMBOL SUMMARY ===")
        print(f"{'Symbol':<12} {'Realized':<10} {'Implied':<10} {'Premium':<10} {'Regime':<15}")
        print("-" * 70)
        
        for symbol, metrics in results.items():
            regime_short = metrics.current_regime.value[:12]
            print(f"{symbol:<12} {metrics.realized_vol_daily:<10.2f} "
                  f"{metrics.implied_vol_current:<10.2f} {metrics.vol_risk_premium:<10.2f} "
                  f"{regime_short:<15}")
        
        # Find extremes
        highest_vol = max(results.items(), key=lambda x: x[1].realized_vol_daily)
        lowest_vol = min(results.items(), key=lambda x: x[1].realized_vol_daily)
        highest_premium = max(results.items(), key=lambda x: x[1].vol_risk_premium)
        
        print(f"\n[INSIGHTS]")
        print(f"Highest Volatility: {highest_vol[0]} ({highest_vol[1].realized_vol_daily:.2f}%)")
        print(f"Lowest Volatility:  {lowest_vol[0]} ({lowest_vol[1].realized_vol_daily:.2f}%)")
        print(f"Highest Vol Premium: {highest_premium[0]} ({highest_premium[1].vol_risk_premium:.2f}%)")


async def test_volatility_analyzer():
    """Run comprehensive volatility analyzer tests"""
    print("STARTING COMPREHENSIVE VOLATILITY ANALYZER TESTING")
    print("=" * 90)
    
    await test_basic_volatility_analysis()
    await test_volatility_regimes()
    await test_volatility_forecasting()
    await test_multiple_symbols()
    
    print(f"\n{'=' * 90}")
    print("VOLATILITY ANALYZER TESTING COMPLETED!")
    print("=" * 90)


if __name__ == "__main__":
    asyncio.run(test_volatility_analyzer())