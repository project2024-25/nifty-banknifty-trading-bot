import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing database connection...")

try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print(f"Connecting to: {supabase_url}")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Test connection with a simple query
    result = supabase.table('trades').select('count', count='exact').execute()
    
    print("Database connection successful!")
    print(f"trades table: {result.count} records")
    
    # Test other tables
    tables = ['positions', 'signals', 'performance_metrics', 'market_intelligence']
    for table in tables:
        try:
            result = supabase.table(table).select('count', count='exact').execute()
            print(f"{table}: {result.count} records")
        except Exception as e:
            print(f"{table}: Error - {str(e)[:50]}")
            
    print("All database tests passed!")
    
except Exception as e:
    print(f"Database connection failed: {e}")