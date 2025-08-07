#!/usr/bin/env python3
import asyncio
from datetime import datetime
from src.strategies.base_strategy import MarketData
from src.intelligence.strategy_selector import AdaptiveStrategySelector
from src.intelligence.dynamic_allocator import DynamicAllocationManager, AllocationMode


async def test_portfolio_allocation():
    print("=" * 80)
    print("TESTING PORTFOLIO ALLOCATION SYSTEM")
    print("=" * 80)
    
    # Initialize components
    selector = AdaptiveStrategySelector()
    allocator = DynamicAllocationManager(total_capital=1000000, max_risk_per_trade=0.02)
    
    # Test market scenario
    market_data = MarketData(
        symbol="NIFTY",
        spot_price=24000.0,
        iv=35.0,  # Good moderate volatility
        volume=500000,
        oi=100000,
        last_updated=datetime.now()
    )
    
    print(f"Test Market: Spot {market_data.spot_price}, IV {market_data.iv}%")
    print(f"Portfolio Capital: Rs.{allocator.total_capital:,}")
    print(f"Max Risk Per Trade: {allocator.max_risk_per_trade:.1%}")
    
    try:
        # Step 1: Generate adaptive signals
        print(f"\n{'-'*60}")
        print("STEP 1: GENERATING ADAPTIVE SIGNALS")
        print(f"{'-'*60}")
        
        signals = await selector.generate_adaptive_signals(market_data)
        
        if not signals:
            print("[ERROR] No signals generated")
            return
        
        print(f"[SUCCESS] Generated {len(signals)} signals:")
        for i, signal in enumerate(signals, 1):
            print(f"  {i}. {signal.strategy_name} - Confidence: {signal.confidence_score:.1%}")
        
        # Step 2: Test different allocation modes
        allocation_modes = [
            AllocationMode.EQUAL_WEIGHT,
            AllocationMode.CONFIDENCE_WEIGHTED,
            AllocationMode.REGIME_ADAPTIVE,
            AllocationMode.KELLY_CRITERION
        ]
        
        # Get market conditions for allocation
        market_conditions = selector.regime_detector.detect_regime(market_data)
        
        for mode in allocation_modes:
            print(f"\n{'-'*60}")
            print(f"TESTING ALLOCATION MODE: {mode.value.upper()}")
            print(f"{'-'*60}")
            
            try:
                # Create portfolio allocation
                portfolio = allocator.allocate_portfolio(signals, market_conditions, mode)
                
                print(f"Portfolio Summary:")
                print(f"  Total Positions: {len(portfolio.positions)}")
                print(f"  Capital Used: Rs.{portfolio.total_capital_used:,.2f}")
                print(f"  Risk Allocated: {portfolio.total_risk_allocated:.1%}")
                print(f"  Expected Return: Rs.{portfolio.expected_return:,.2f}")
                print(f"  Max Portfolio Loss: Rs.{portfolio.max_portfolio_loss:,.2f}")
                
                if portfolio.positions:
                    print(f"\nPosition Details:")
                    print(f"{'Strategy':<18} {'Size':<6} {'Capital':<12} {'Risk':<8} {'Max Loss':<12}")
                    print("-" * 70)
                    
                    for pos in portfolio.positions:
                        print(f"{pos.signal.strategy_name:<18} "
                              f"{pos.position_size:<6.0f} "
                              f"Rs.{pos.capital_allocation:<11,.0f} "
                              f"{pos.risk_allocation:<7.1%} "
                              f"Rs.{pos.max_loss_per_position:<11,.0f}")
                    
                    print(f"\nSample Position Reasoning:")
                    print(f"  {portfolio.positions[0].reasoning}")
                
                # Update allocator state for next test
                allocator.update_positions(portfolio)
                
                # Show portfolio summary
                summary = allocator.get_portfolio_summary()
                print(f"\nPortfolio Utilization:")
                print(f"  Capital: {summary['utilization']['capital']:.1%}")
                print(f"  Risk: {summary['utilization']['risk']:.1%}")
                
            except Exception as e:
                print(f"[ERROR] Failed to test {mode.value}: {e}")
                import traceback
                traceback.print_exc()
        
        # Step 3: Test regime-specific allocation
        print(f"\n{'='*80}")
        print("TESTING REGIME-SPECIFIC SCENARIOS")
        print(f"{'='*80}")
        
        # Test different market regimes
        regime_scenarios = [
            {"name": "Bull Trending", "iv": 18, "volume": 700000},
            {"name": "Bear Volatile", "iv": 50, "volume": 900000}, 
            {"name": "High Uncertainty", "iv": 60, "volume": 400000},
        ]
        
        for scenario in regime_scenarios:
            print(f"\n{'-'*50}")
            print(f"SCENARIO: {scenario['name']}")
            print(f"{'-'*50}")
            
            test_data = MarketData(
                symbol="NIFTY",
                spot_price=24000.0,
                iv=scenario["iv"],
                volume=scenario["volume"],
                oi=100000,
                last_updated=datetime.now()
            )
            
            try:
                # Reset allocator for each scenario
                test_allocator = DynamicAllocationManager(total_capital=1000000)
                
                # Get regime-specific signals
                regime_signals = await selector.generate_adaptive_signals(test_data)
                
                if regime_signals:
                    regime_conditions = selector.regime_detector.detect_regime(test_data)
                    regime_portfolio = test_allocator.allocate_portfolio(
                        regime_signals, regime_conditions, AllocationMode.REGIME_ADAPTIVE
                    )
                    
                    print(f"Detected Regime: {regime_conditions.regime.value}")
                    print(f"Strategies Selected: {len(regime_portfolio.positions)}")
                    
                    if regime_portfolio.positions:
                        top_strategy = regime_portfolio.positions[0]
                        print(f"Top Strategy: {top_strategy.signal.strategy_name}")
                        print(f"Position Size: {top_strategy.position_size}")
                        print(f"Risk Allocation: {top_strategy.risk_allocation:.1%}")
                        
                else:
                    print("No signals generated for this regime")
                    
            except Exception as e:
                print(f"[ERROR] Failed regime test: {e}")
        
        print(f"\n{'='*80}")
        print("PORTFOLIO ALLOCATION TESTING COMPLETED")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"[ERROR] Portfolio allocation test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_portfolio_allocation())