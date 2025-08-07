#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
import random
from src.intelligence.performance_attribution import (
    PerformanceAttributionEngine, AttributionPeriod, TradePerformance
)
from src.intelligence.market_regime import MarketRegime, VolatilityRegime


def create_mock_trade_data():
    """Create mock trade data for testing"""
    
    # Define some sample strategies and their typical performance
    strategies = [
        {"name": "Iron Condor", "win_rate": 0.75, "avg_win": 200, "avg_loss": -800},
        {"name": "Bull Put Spread", "win_rate": 0.70, "avg_win": 150, "avg_loss": -600},
        {"name": "Butterfly Spread", "win_rate": 0.65, "avg_win": 180, "avg_loss": -700},
        {"name": "Long Straddle", "win_rate": 0.45, "avg_win": 1200, "avg_loss": -400},
        {"name": "Short Straddle", "win_rate": 0.80, "avg_win": 300, "avg_loss": -1000}
    ]
    
    regimes = [
        MarketRegime.BULL_TRENDING,
        MarketRegime.BEAR_TRENDING, 
        MarketRegime.SIDEWAYS_LOW_VOL,
        MarketRegime.SIDEWAYS_HIGH_VOL,
        MarketRegime.BULL_VOLATILE
    ]
    
    volatilities = [
        VolatilityRegime.LOW,
        VolatilityRegime.MEDIUM,
        VolatilityRegime.HIGH,
        VolatilityRegime.EXTREME
    ]
    
    mock_trades = []
    
    # Generate trades over the past 90 days
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(200):  # Generate 200 mock trades
        strategy = random.choice(strategies)
        regime = random.choice(regimes)
        volatility = random.choice(volatilities)
        
        # Create trade based on strategy characteristics
        is_winner = random.random() < strategy["win_rate"]
        
        if is_winner:
            pnl = strategy["avg_win"] + random.randint(-50, 100)
        else:
            pnl = strategy["avg_loss"] + random.randint(-200, 100)
        
        entry_time = base_date + timedelta(days=random.randint(0, 90))
        exit_time = entry_time + timedelta(days=random.randint(1, 30))
        
        trade_data = {
            'trade_id': f'MOCK_{i+1:03d}',
            'strategy_name': strategy["name"],
            'symbol': random.choice(['NIFTY', 'BANKNIFTY']),
            'entry_time': entry_time,
            'exit_time': exit_time,
            'position_size': random.randint(1, 5),
            'max_profit': abs(pnl) if pnl > 0 else random.randint(100, 500),
            'max_loss': abs(pnl) if pnl < 0 else random.randint(200, 1000),
            'actual_pnl': pnl,
            'is_closed': True,
            'close_reason': 'Expired' if random.random() > 0.3 else 'Manual'
        }
        
        regime_context = {
            'regime': regime,
            'volatility_regime': volatility,
            'confidence': random.uniform(0.4, 0.95)
        }
        
        mock_trades.append((trade_data, regime_context))
    
    return mock_trades


async def test_performance_attribution():
    print("=" * 80)
    print("TESTING PERFORMANCE ATTRIBUTION ENGINE")
    print("=" * 80)
    
    # Initialize the attribution engine
    attribution_engine = PerformanceAttributionEngine()
    
    try:
        # Generate and add mock trades
        print("\n[STEP 1] Generating mock trade data...")
        mock_trades = create_mock_trade_data()
        
        for trade_data, regime_context in mock_trades:
            attribution_engine.add_trade_performance(trade_data, regime_context)
        
        print(f"[SUCCESS] Added {len(mock_trades)} mock trades to attribution engine")
        
        # Test strategy attribution
        print(f"\n[STEP 2] Calculating strategy attributions...")
        
        strategies = ["Iron Condor", "Bull Put Spread", "Butterfly Spread", "Long Straddle"]
        
        for strategy in strategies:
            print(f"\n--- {strategy} Attribution ---")
            
            try:
                attribution = attribution_engine.calculate_strategy_attribution(
                    strategy, AttributionPeriod.MONTHLY
                )
                
                print(f"Period: {attribution.period_start.date()} to {attribution.period_end.date()}")
                print(f"Total Trades: {attribution.total_trades}")
                print(f"Win Rate: {attribution.win_rate:.1%}")
                print(f"Total P&L: Rs.{attribution.total_pnl:,.2f}")
                print(f"Average Win: Rs.{attribution.average_win:,.2f}")
                print(f"Average Loss: Rs.{attribution.average_loss:,.2f}")
                print(f"Profit Factor: {attribution.profit_factor:.2f}")
                print(f"Sharpe Ratio: {attribution.sharpe_ratio:.3f}")
                
                if attribution.regime_performance:
                    print(f"Regime Performance:")
                    for regime, pnl in attribution.regime_performance.items():
                        print(f"  {regime}: Rs.{pnl:,.2f}")
                
                print(f"Alpha Contribution: Rs.{attribution.alpha_contribution:,.2f}")
                print(f"Regime Contribution: Rs.{attribution.regime_contribution:,.2f}")
                
            except Exception as e:
                print(f"[ERROR] Strategy attribution failed for {strategy}: {e}")
        
        # Test regime attribution
        print(f"\n[STEP 3] Calculating regime attributions...")
        
        regimes_to_test = [
            MarketRegime.SIDEWAYS_LOW_VOL,
            MarketRegime.BULL_TRENDING,
            MarketRegime.SIDEWAYS_HIGH_VOL
        ]
        
        for regime in regimes_to_test:
            print(f"\n--- {regime.value.replace('_', ' ').title()} Regime ---")
            
            try:
                regime_attribution = attribution_engine.calculate_regime_attribution(
                    regime, AttributionPeriod.MONTHLY
                )
                
                print(f"Strategies Used: {', '.join(regime_attribution.strategies_used)}")
                print(f"Total Regime P&L: Rs.{regime_attribution.total_regime_pnl:,.2f}")
                print(f"Average P&L: Rs.{regime_attribution.average_regime_pnl:,.2f}")
                print(f"Win Rate: {regime_attribution.regime_win_rate:.1%}")
                
                if regime_attribution.best_strategy:
                    print(f"Best Strategy: {regime_attribution.best_strategy} (Rs.{regime_attribution.best_strategy_pnl:,.2f})")
                
                if regime_attribution.worst_strategy:
                    print(f"Worst Strategy: {regime_attribution.worst_strategy} (Rs.{regime_attribution.worst_strategy_pnl:,.2f})")
                
            except Exception as e:
                print(f"[ERROR] Regime attribution failed for {regime}: {e}")
        
        # Test comprehensive performance summary
        print(f"\n[STEP 4] Generating performance summary...")
        
        try:
            summary = attribution_engine.get_performance_summary(AttributionPeriod.MONTHLY)
            
            if 'error' not in summary:
                print(f"\n=== PERFORMANCE SUMMARY ({summary['period']}) ===")
                
                overall = summary['overall_performance']
                print(f"Total P&L: Rs.{overall['total_pnl']:,.2f}")
                print(f"Total Trades: {overall['total_trades']}")
                print(f"Win Rate: {overall['win_rate']:.1%}")
                print(f"Average Trade P&L: Rs.{summary['statistics']['average_trade_pnl']:,.2f}")
                
                print(f"\n=== STRATEGY PERFORMANCE ===")
                for strategy, perf in summary['strategy_performance'].items():
                    print(f"{strategy}:")
                    print(f"  P&L: Rs.{perf['total_pnl']:,.2f}, Trades: {perf['trades']}, Win Rate: {perf['win_rate']:.1%}")
                
                print(f"\n=== REGIME PERFORMANCE ===")
                for regime, perf in summary['regime_performance'].items():
                    print(f"{regime.replace('_', ' ').title()}:")
                    print(f"  P&L: Rs.{perf['total_pnl']:,.2f}, Win Rate: {perf['win_rate']:.1%}")
                    print(f"  Best Strategy: {perf['best_strategy']}, Strategies Used: {perf['strategies_used']}")
                
                performers = summary['top_performers']
                print(f"\n=== TOP PERFORMERS ===")
                print(f"Best Strategy: {performers['best_strategy']} (Rs.{performers['best_strategy_pnl']:,.2f})")
                print(f"Worst Strategy: {performers['worst_strategy']}")
                
                stats = summary['statistics']
                print(f"\n=== STATISTICS ===")
                print(f"Strategies Active: {stats['strategies_active']}")
                print(f"Regimes Encountered: {stats['regimes_encountered']}")
                
            else:
                print(f"[ERROR] Performance summary failed: {summary['error']}")
        
        except Exception as e:
            print(f"[ERROR] Performance summary failed: {e}")
        
        # Test different attribution periods
        print(f"\n[STEP 5] Testing different attribution periods...")
        
        periods_to_test = [
            AttributionPeriod.WEEKLY,
            AttributionPeriod.MONTHLY,
            AttributionPeriod.QUARTERLY
        ]
        
        test_strategy = "Iron Condor"
        
        for period in periods_to_test:
            try:
                attribution = attribution_engine.calculate_strategy_attribution(test_strategy, period)
                print(f"{period.value}: {attribution.total_trades} trades, Rs.{attribution.total_pnl:,.2f} P&L")
            
            except Exception as e:
                print(f"[ERROR] {period.value} attribution failed: {e}")
        
        print(f"\n[SUCCESS] Performance attribution testing completed!")
        
    except Exception as e:
        print(f"[ERROR] Performance attribution test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_trade_performance_tracking():
    print(f"\n{'='*80}")
    print("TESTING TRADE PERFORMANCE TRACKING")
    print(f"{'='*80}")
    
    attribution_engine = PerformanceAttributionEngine()
    
    # Test adding individual trades
    sample_trades = [
        {
            'trade_id': 'TEST_001',
            'strategy_name': 'Iron Condor',
            'symbol': 'NIFTY',
            'entry_time': datetime.now() - timedelta(days=10),
            'exit_time': datetime.now() - timedelta(days=3),
            'position_size': 2,
            'max_profit': 400,
            'max_loss': -800,
            'actual_pnl': 350,
            'is_closed': True,
            'close_reason': 'Profit target'
        },
        {
            'trade_id': 'TEST_002', 
            'strategy_name': 'Bull Put Spread',
            'symbol': 'BANKNIFTY',
            'entry_time': datetime.now() - timedelta(days=15),
            'exit_time': datetime.now() - timedelta(days=8),
            'position_size': 3,
            'max_profit': 300,
            'max_loss': -600,
            'actual_pnl': -550,
            'is_closed': True,
            'close_reason': 'Stop loss'
        }
    ]
    
    regime_contexts = [
        {
            'regime': MarketRegime.SIDEWAYS_LOW_VOL,
            'volatility_regime': VolatilityRegime.MEDIUM,
            'confidence': 0.85
        },
        {
            'regime': MarketRegime.BULL_TRENDING,
            'volatility_regime': VolatilityRegime.LOW,
            'confidence': 0.72
        }
    ]
    
    print(f"Adding {len(sample_trades)} sample trades...")
    
    for i, trade in enumerate(sample_trades):
        attribution_engine.add_trade_performance(trade, regime_contexts[i])
        print(f"[SUCCESS] Added trade {trade['trade_id']}: {trade['strategy_name']}, P&L: Rs.{trade['actual_pnl']}")
    
    # Test trade performance calculation
    print(f"\nTrade history length: {len(attribution_engine.trade_history)}")
    
    for trade_perf in attribution_engine.trade_history:
        print(f"Trade {trade_perf.trade_id}:")
        print(f"  Strategy: {trade_perf.strategy_name}")
        print(f"  Days Held: {trade_perf.days_held}")
        print(f"  R:R Ratio: {trade_perf.risk_reward_ratio:.2f}")
        print(f"  Entry Regime: {trade_perf.entry_regime.value if trade_perf.entry_regime else 'N/A'}")
        print(f"  Entry Confidence: {trade_perf.entry_confidence:.1%}")


if __name__ == "__main__":
    asyncio.run(test_performance_attribution())
    asyncio.run(test_trade_performance_tracking())