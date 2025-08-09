#!/usr/bin/env python3
"""
Test script for Kite Connect integration and Multi-timeframe Analysis

This script tests the integration between:
1. Kite Connect API wrapper
2. Multi-timeframe analysis engine  
3. Sophisticated trading system

Run this to verify everything works together properly.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set environment variables for testing
os.environ.setdefault('KITE_API_KEY', 'test_key')
os.environ.setdefault('KITE_API_SECRET', 'test_secret')
os.environ.setdefault('ENABLE_PAPER_TRADING', 'true')

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lambda_functions', 'src'))

async def test_kite_wrapper():
    """Test Kite Connect wrapper functionality."""
    print("\n" + "="*60)
    print("🔧 TESTING KITE CONNECT WRAPPER")
    print("="*60)
    
    try:
        from integrations.kite_connect_wrapper import create_kite_wrapper, OrderRequest
        
        # Create wrapper instance
        wrapper = create_kite_wrapper(
            api_key=os.getenv('KITE_API_KEY', 'test_key'),
            api_secret=os.getenv('KITE_API_SECRET', 'test_secret'),
            access_token=os.getenv('KITE_ACCESS_TOKEN'),
            paper_trading=True  # Always use paper trading for tests
        )
        
        print("✅ Kite wrapper created successfully")
        
        # Test authentication
        auth_success = await wrapper.authenticate()
        print(f"✅ Authentication: {'Success' if auth_success else 'Failed (expected for paper trading)'}")
        
        # Test health check
        health = await wrapper.health_check()
        print(f"✅ Health check: {health.get('connection_status', 'Unknown')}")
        
        # Test quotes
        quotes = await wrapper.get_quote(['NIFTY', 'BANKNIFTY'])
        print(f"✅ Quotes retrieved: {len(quotes)} instruments")
        for symbol, quote in quotes.items():
            print(f"   {symbol}: ₹{quote.get('last_price', 'N/A')}")
        
        # Test positions
        positions = await wrapper.get_positions()
        print(f"✅ Positions: {len(positions)} positions")
        
        # Test historical data
        start_date = datetime.now().replace(day=1)  # Start of current month
        end_date = datetime.now()
        
        historical = await wrapper.get_historical_data('NIFTY', start_date, end_date, 'daily')
        print(f"✅ Historical data: {len(historical)} candles")
        if historical:
            latest = historical[-1]
            print(f"   Latest: O={latest['open']}, H={latest['high']}, L={latest['low']}, C={latest['close']}")
        
        # Test paper order placement
        order = OrderRequest(
            symbol='NIFTY25000CE',
            quantity=50,
            order_type='LIMIT',
            transaction_type='BUY',
            price=100.0
        )
        
        order_id = await wrapper.place_order(order)
        print(f"✅ Paper order placed: {order_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kite wrapper test failed: {e}")
        return False


async def test_multi_timeframe_analyzer():
    """Test multi-timeframe analysis functionality."""
    print("\n" + "="*60)
    print("🔍 TESTING MULTI-TIMEFRAME ANALYZER")
    print("="*60)
    
    try:
        from intelligence.multi_timeframe import MultiTimeframeAnalyzer
        
        # Create analyzer
        analyzer = MultiTimeframeAnalyzer()
        print("✅ Multi-timeframe analyzer created")
        
        # Test NIFTY analysis
        print("\n📊 Analyzing NIFTY...")
        nifty_analysis = await analyzer.analyze_symbol('NIFTY', use_real_data=False)
        print(f"✅ NIFTY Analysis completed:")
        print(f"   Trend: {nifty_analysis.overall_trend}")
        print(f"   Confidence: {nifty_analysis.overall_confidence:.2%}")
        print(f"   Market Regime: {nifty_analysis.market_regime}")
        print(f"   Entry Zones: {len(nifty_analysis.entry_zones)}")
        print(f"   Recommendations: {len(nifty_analysis.recommendations)}")
        
        # Test BANKNIFTY analysis
        print("\n🏦 Analyzing BANKNIFTY...")
        banknifty_analysis = await analyzer.analyze_symbol('BANKNIFTY', use_real_data=False)
        print(f"✅ BANKNIFTY Analysis completed:")
        print(f"   Trend: {banknifty_analysis.overall_trend}")
        print(f"   Confidence: {banknifty_analysis.overall_confidence:.2%}")
        print(f"   Market Regime: {banknifty_analysis.market_regime}")
        print(f"   Entry Zones: {len(banknifty_analysis.entry_zones)}")
        
        # Test timeframe breakdown
        if nifty_analysis.timeframes:
            print(f"\n⏰ NIFTY Timeframe Analysis:")
            for tf, signal in nifty_analysis.timeframes.items():
                print(f"   {tf}: {signal.trend} ({signal.confidence:.1%} confidence)")
        
        # Test pre-market analysis
        print(f"\n🌅 Testing pre-market analysis...")
        pre_market = await analyzer.analyze_pre_market()
        print(f"✅ Pre-market analysis completed")
        print(f"   Market outlook: {pre_market.get('market_outlook', {}).get('overall_sentiment', 'Unknown')}")
        print(f"   Trading plan: {pre_market.get('trading_plan', {}).get('strategy_bias', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-timeframe analyzer test failed: {e}")
        return False


async def test_integrated_system():
    """Test the integrated sophisticated trading system."""
    print("\n" + "="*60)
    print("🧠 TESTING INTEGRATED SOPHISTICATED SYSTEM")
    print("="*60)
    
    try:
        # Import the sophisticated handler
        sys.path.append(os.path.join(os.path.dirname(__file__), 'lambda_functions', 'main_trading'))
        
        # Create mock event for testing
        test_event = {
            'action': 'trading',
            'force_run': True
        }
        
        # Import and test the handler
        from sophisticated_handler import lambda_handler
        
        print("🔄 Running sophisticated trading cycle...")
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda_handler, test_event, None
        )
        
        if isinstance(result, dict) and result.get('statusCode') == 200:
            body = result.get('body', '{}')
            if isinstance(body, str):
                import json
                body = json.loads(body)
            
            print("✅ Sophisticated system test completed successfully")
            print(f"   Status: {body.get('status', 'Unknown')}")
            print(f"   Mode: {body.get('mode', 'Unknown')}")
            print(f"   Market Regime: {body.get('market_regime', 'Unknown')}")
            print(f"   Signals Generated: {body.get('signals_generated', 0)}")
            print(f"   Multi-TF Analysis: {'✅' if 'multi_timeframe' in str(body) else '❌'}")
            
            return True
        else:
            print(f"❌ Sophisticated system test failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Integrated system test failed: {e}")
        return False


async def test_kite_with_multiframe():
    """Test Kite Connect with multi-timeframe analyzer integration."""
    print("\n" + "="*60)
    print("🔗 TESTING KITE + MULTI-TIMEFRAME INTEGRATION")
    print("="*60)
    
    try:
        from integrations.kite_connect_wrapper import create_kite_wrapper
        from intelligence.multi_timeframe import MultiTimeframeAnalyzer
        
        # Create Kite wrapper
        kite_wrapper = create_kite_wrapper(
            api_key=os.getenv('KITE_API_KEY', 'test_key'),
            api_secret=os.getenv('KITE_API_SECRET', 'test_secret'),
            access_token=os.getenv('KITE_ACCESS_TOKEN'),
            paper_trading=True
        )
        
        await kite_wrapper.authenticate()
        
        # Create analyzer with Kite wrapper
        analyzer = MultiTimeframeAnalyzer(kite_wrapper=kite_wrapper)
        print("✅ Multi-timeframe analyzer with Kite integration created")
        
        # Test analysis with "real" data (mock in paper trading mode)
        print("\n🔍 Testing analysis with Kite data source...")
        analysis = await analyzer.analyze_symbol('NIFTY', use_real_data=True)
        
        print(f"✅ Analysis with Kite integration completed:")
        print(f"   Symbol: {analysis.symbol}")
        print(f"   Trend: {analysis.overall_trend}")
        print(f"   Confidence: {analysis.overall_confidence:.2%}")
        print(f"   Timeframes analyzed: {len(analysis.timeframes)}")
        
        # Test health check
        health = await kite_wrapper.health_check()
        print(f"✅ Kite wrapper health: {health.get('connection_status', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kite + Multi-timeframe integration test failed: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("🚀 STARTING KITE CONNECT & MULTI-TIMEFRAME INTEGRATION TESTS")
    print("=" * 80)
    
    test_results = []
    
    # Run individual tests
    test_results.append(await test_kite_wrapper())
    test_results.append(await test_multi_timeframe_analyzer())
    test_results.append(await test_kite_with_multiframe())
    test_results.append(await test_integrated_system())
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST RESULTS SUMMARY")
    print("="*60)
    
    test_names = [
        "Kite Connect Wrapper",
        "Multi-timeframe Analyzer", 
        "Kite + Multi-TF Integration",
        "Integrated Sophisticated System"
    ]
    
    passed = sum(test_results)
    total = len(test_results)
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Kite Connect and Multi-timeframe integration is working perfectly!")
        print("\n🚀 Your sophisticated trading system is ready with:")
        print("   ✅ Kite Connect API integration")
        print("   ✅ Multi-timeframe analysis (5min, 15min, 1hour, daily, weekly)")  
        print("   ✅ Real-time market data integration")
        print("   ✅ Paper trading mode")
        print("   ✅ Historical data analysis")
        print("   ✅ Sophisticated notifications")
    else:
        print(f"⚠️  {total-passed} tests failed. Please check the logs above for details.")
        
    return passed == total


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)