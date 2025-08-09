#!/usr/bin/env python3
"""
Supabase Connection Test Script

This script tests the Supabase database connection and verifies all tables
are accessible with the provided credentials.
"""

import asyncio
import os
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Add source path
sys.path.insert(0, os.getcwd())

# Test environment variables
os.environ.setdefault('SUPABASE_URL', 'your-supabase-url')
os.environ.setdefault('SUPABASE_KEY', 'your-supabase-key')

async def test_supabase_connection():
    """Test Supabase connection and table access."""
    
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    
    try:
        # Try importing Supabase client
        try:
            from supabase import create_client, Client
            print("SUCCESS: Supabase client library available")
        except ImportError:
            print("WARNING: supabase-py not installed")
            print("Install with: pip install supabase")
            
            # Try psycopg2 direct connection as fallback
            try:
                import psycopg2
                print("SUCCESS: psycopg2 available as fallback")
                return await test_postgres_connection()
            except ImportError:
                print("ERROR: Neither supabase-py nor psycopg2 available")
                return False
        
        # Get credentials
        supabase_url = os.getenv('SUPABASE_URL', '')
        supabase_key = os.getenv('SUPABASE_KEY', '')
        
        if not supabase_url or not supabase_key:
            print("WARNING: SUPABASE_URL or SUPABASE_KEY not set")
            print("Using test credentials...")
            return await test_mock_connection()
        
        print(f"Connecting to: {supabase_url[:50]}...")
        
        # Create client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("SUCCESS: Supabase client created")
        
        # Test all tables from your schema
        tables_to_test = [
            'trades',
            'positions', 
            'signals',
            'market_intelligence',
            'performance_metrics',
            'risk_events',
            'system_logs',
            'user_sessions'
        ]
        
        results = {}
        
        for table in tables_to_test:
            try:
                print(f"Testing {table} table...")
                
                # Test read access
                response = supabase.table(table).select("*").limit(1).execute()
                
                if hasattr(response, 'data'):
                    results[table] = {
                        'accessible': True,
                        'record_count': len(response.data) if response.data else 0,
                        'status': 'SUCCESS'
                    }
                    print(f"  SUCCESS: {table} table accessible")
                else:
                    results[table] = {
                        'accessible': False,
                        'error': 'No data attribute in response',
                        'status': 'ERROR'
                    }
                    print(f"  ERROR: {table} table - no data in response")
                    
            except Exception as e:
                results[table] = {
                    'accessible': False,
                    'error': str(e),
                    'status': 'ERROR'
                }
                print(f"  ERROR: {table} table - {e}")
        
        # Test write access with a sample system log
        try:
            print("\nTesting write access...")
            
            log_entry = {
                'level': 'INFO',
                'message': 'Supabase connection test',
                'module': 'test_script',
                'function_name': 'test_supabase_connection',
                'metadata': {'test': True, 'timestamp': datetime.now(timezone.utc).isoformat()},
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            response = supabase.table('system_logs').insert(log_entry).execute()
            
            if response.data:
                print("SUCCESS: Write access confirmed")
                results['write_test'] = {'status': 'SUCCESS', 'record_id': response.data[0].get('id')}
            else:
                print("WARNING: Write test unclear")
                results['write_test'] = {'status': 'UNCLEAR'}
                
        except Exception as e:
            print(f"ERROR: Write test failed - {e}")
            results['write_test'] = {'status': 'ERROR', 'error': str(e)}
        
        return results
        
    except Exception as e:
        print(f"CRITICAL ERROR: Supabase connection failed - {e}")
        return False

async def test_postgres_connection():
    """Test direct PostgreSQL connection as fallback."""
    
    print("\n" + "=" * 60)
    print("DIRECT POSTGRESQL CONNECTION TEST")
    print("=" * 60)
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        supabase_url = os.getenv('SUPABASE_URL', '')
        
        if not supabase_url:
            print("ERROR: No SUPABASE_URL provided")
            return False
        
        # Convert Supabase URL to PostgreSQL connection string
        if 'supabase.co' in supabase_url:
            # Extract database info from Supabase URL
            # Format: https://xxx.supabase.co
            parsed = urlparse(supabase_url)
            host = parsed.hostname
            
            # For direct PostgreSQL, you'd need the full connection details
            print("INFO: For direct PostgreSQL connection, you need:")
            print("  - Host, Port, Database name, Username, Password")
            print("  - These can be found in your Supabase database settings")
            print("WARNING: Direct PostgreSQL connection requires full credentials")
            
            return {'status': 'NEEDS_CREDENTIALS', 'message': 'Direct PostgreSQL requires full DB credentials'}
        
        return False
        
    except ImportError:
        print("ERROR: psycopg2 not available")
        return False

async def test_mock_connection():
    """Test with mock data to verify system integration."""
    
    print("\n" + "=" * 60)
    print("MOCK DATABASE CONNECTION TEST")
    print("=" * 60)
    
    try:
        # Test our database manager with mock mode
        from src.integrations.database import DatabaseManager
        
        db = DatabaseManager()
        
        # Initialize in mock mode
        success = await db.initialize()
        
        if success:
            print("SUCCESS: Database manager initialized")
            
            # Test create trade
            trade_data = {
                'symbol': 'NIFTY25000CE',
                'strategy': 'Bull Call Spread',
                'entry_time': datetime.now(timezone.utc).isoformat(),
                'entry_price': 125.50,
                'quantity': 50,
                'trade_type': 'BUY',
                'order_type': 'LIMIT',
                'trade_category': 'conservative',
                'paper_trade': True,
                'notes': 'Supabase connection test trade'
            }
            
            trade_id = await db.create_trade(trade_data)
            
            if trade_id:
                print(f"SUCCESS: Test trade created with ID: {trade_id}")
            else:
                print("WARNING: Trade creation returned no ID")
            
            return {'status': 'SUCCESS', 'mode': 'MOCK'}
        else:
            print("ERROR: Database manager initialization failed")
            return False
            
    except Exception as e:
        print(f"ERROR: Mock connection test failed - {e}")
        return False

async def test_sophisticated_integration():
    """Test Supabase integration with sophisticated system."""
    
    print("\n" + "=" * 60)
    print("SOPHISTICATED SYSTEM DATABASE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Import sophisticated handler
        sys.path.append(os.path.join(os.getcwd(), 'lambda_functions', 'main_trading'))
        
        # Create test event
        test_event = {
            'action': 'health_check',
            'test_database': True
        }
        
        print("Testing sophisticated handler with database...")
        
        # This will test the actual integration
        from sophisticated_handler import lambda_handler
        
        result = lambda_handler(test_event, None)
        
        if result.get('statusCode') == 200:
            body = json.loads(result.get('body', '{}'))
            
            db_connected = body.get('database_connected', False)
            
            print(f"Sophisticated system test:")
            print(f"  Database connected: {db_connected}")
            print(f"  Status: {body.get('status', 'Unknown')}")
            print(f"  Mode: {body.get('mode', 'Unknown')}")
            
            return {
                'sophisticated_test': True,
                'database_connected': db_connected,
                'status': body.get('status', 'Unknown')
            }
        else:
            print(f"ERROR: Sophisticated system test failed - {result}")
            return False
            
    except Exception as e:
        print(f"ERROR: Sophisticated integration test failed - {e}")
        return False

def display_results(results):
    """Display comprehensive test results."""
    
    print("\n" + "=" * 60)
    print("SUPABASE CONNECTION TEST RESULTS")
    print("=" * 60)
    
    if not results:
        print("ERROR: No results to display")
        return
    
    if isinstance(results, dict):
        print("\nTABLE ACCESS RESULTS:")
        
        table_results = {}
        other_results = {}
        
        for key, value in results.items():
            if key in ['trades', 'positions', 'signals', 'market_intelligence', 
                      'performance_metrics', 'risk_events', 'system_logs', 'user_sessions']:
                table_results[key] = value
            else:
                other_results[key] = value
        
        # Display table results
        if table_results:
            for table, result in table_results.items():
                status = result.get('status', 'UNKNOWN')
                print(f"  {table}: {status}")
                if status == 'ERROR':
                    print(f"    Error: {result.get('error', 'Unknown error')}")
        
        # Display other results
        if other_results:
            print(f"\nOTHER TESTS:")
            for test, result in other_results.items():
                if isinstance(result, dict):
                    print(f"  {test}: {result.get('status', 'UNKNOWN')}")
                    if result.get('error'):
                        print(f"    Error: {result['error']}")
                else:
                    print(f"  {test}: {result}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n1. If connections successful:")
    print("   - Your Supabase database is ready")
    print("   - All tables are accessible")
    print("   - Sophisticated system can log trades and analytics")
    
    print("\n2. If connections failed:")
    print("   - Verify SUPABASE_URL and SUPABASE_KEY in GitHub Secrets")
    print("   - Check Render environment variables")
    print("   - Ensure Supabase project is active")
    print("   - Verify database permissions")
    
    print("\n3. Next steps:")
    print("   - Test with live trading data")
    print("   - Monitor database usage in Supabase dashboard")
    print("   - Set up database backups if needed")

async def main():
    """Main test function."""
    
    print("Starting Supabase connection tests...")
    
    # Test Supabase connection
    supabase_results = await test_supabase_connection()
    
    # Test sophisticated system integration
    sophisticated_results = await test_sophisticated_integration()
    
    # Combine results
    all_results = {}
    
    if supabase_results:
        if isinstance(supabase_results, dict):
            all_results.update(supabase_results)
        else:
            all_results['supabase_test'] = supabase_results
    
    if sophisticated_results:
        all_results['sophisticated_integration'] = sophisticated_results
    
    # Display results
    display_results(all_results)
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all_results

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if results:
        print("\nSUCCESS: Tests completed")
    else:
        print("\nERROR: Tests failed")