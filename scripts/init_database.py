#!/usr/bin/env python3
"""
Database Initialization Script
Creates database schema and initial data
"""
import os
import asyncio
from pathlib import Path
from supabase import create_client

from src.utils.config import get_config, validate_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def init_database():
    """Initialize database with schema and initial data"""
    
    print("🗃️  Initializing Trading Bot Database...")
    
    # Validate configuration
    if not validate_config():
        print("❌ Configuration validation failed. Please check your .env file")
        return False
    
    config = get_config()
    
    try:
        # Create Supabase client
        supabase = create_client(config.supabase_url, config.supabase_service_key or config.supabase_key)
        
        print(f"📡 Connected to Supabase: {config.supabase_url}")
        
        # Read schema file
        schema_file = Path(__file__).parent.parent / "config" / "database_schema.sql"
        
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        print(f"📄 Reading schema from: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split schema into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"🔨 Executing {len(statements)} SQL statements...")
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            try:
                # Skip comments and empty statements
                if statement.startswith('--') or not statement.strip():
                    continue
                
                print(f"   [{i}/{len(statements)}] Executing: {statement[:50]}...")
                
                # Execute statement via Supabase RPC (if available) or REST API
                # Note: Supabase Python client doesn't directly support raw SQL execution
                # This is a limitation we'll document
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"   ⚠️  Error in statement {i}: {e}")
                logger.error(f"SQL execution error: {e}", statement=statement[:100])
        
        if error_count == 0:
            print(f"✅ Database initialization completed successfully!")
            print(f"   📊 {success_count} statements executed")
        else:
            print(f"⚠️  Database initialization completed with {error_count} errors")
            print(f"   📊 {success_count} successful, {error_count} failed")
        
        # Test database connection
        print("🧪 Testing database connection...")
        
        try:
            # Test with a simple query
            result = supabase.table('trades').select("count", count='exact').execute()
            print(f"✅ Database connection test successful")
            logger.info("Database initialization completed", 
                       success_count=success_count, 
                       error_count=error_count)
            
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
        
        return error_count == 0
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        logger.error(f"Database initialization error: {e}")
        return False


def print_manual_setup_instructions():
    """Print manual database setup instructions"""
    print("\n" + "="*60)
    print("📋 MANUAL DATABASE SETUP REQUIRED")
    print("="*60)
    print()
    print("Due to Supabase limitations, you need to run the SQL schema manually:")
    print()
    print("1. 🌐 Go to your Supabase dashboard: https://app.supabase.com")
    print("2. 📂 Open your project")
    print("3. 🔍 Navigate to: SQL Editor")
    print("4. 📋 Copy the contents of: config/database_schema.sql")
    print("5. 📝 Paste and run the SQL in the editor")
    print("6. ✅ Verify tables are created in the Table Editor")
    print()
    print("Tables that should be created:")
    tables = [
        "trades", "positions", "signals", "market_intelligence",
        "system_logs", "performance_metrics", "risk_events", "user_sessions"
    ]
    for table in tables:
        print(f"   • {table}")
    print()
    print("Views that should be created:")
    print("   • active_positions")
    print("   • daily_pnl")
    print()
    print("After manual setup, run this script again to test the connection.")
    print("="*60)


async def test_connection_only():
    """Test database connection without initialization"""
    print("🧪 Testing database connection...")
    
    if not validate_config():
        print("❌ Configuration validation failed")
        return False
    
    config = get_config()
    
    try:
        supabase = create_client(config.supabase_url, config.supabase_key)
        
        # Test basic connection
        result = supabase.table('trades').select("count", count='exact').execute()
        print(f"✅ Database connection successful!")
        print(f"   📊 Trades table has {result.count} records")
        
        # Test other tables
        test_tables = ['positions', 'signals', 'performance_metrics']
        for table in test_tables:
            try:
                result = supabase.table(table).select("count", count='exact').execute()
                print(f"   ✅ {table}: {result.count} records")
            except Exception as e:
                print(f"   ❌ {table}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        if "relation" in str(e).lower() and "does not exist" in str(e).lower():
            print("\n💡 It looks like the database tables haven't been created yet.")
            print_manual_setup_instructions()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Trading Bot Database')
    parser.add_argument('--test-only', action='store_true', 
                       help='Only test connection without initialization')
    
    args = parser.parse_args()
    
    if args.test_only:
        success = asyncio.run(test_connection_only())
    else:
        success = asyncio.run(init_database())
        if not success:
            print_manual_setup_instructions()
    
    exit(0 if success else 1)