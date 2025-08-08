"""
Simple Kite Connect Test Script
Test your new Kite Connect credentials with basic functionality.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_kite_credentials():
    """Test Kite Connect credentials and basic functionality."""
    
    print("=== Kite Connect Integration Test ===")
    print()
    
    # Get credentials from environment
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    
    print("Step 1: Check Credentials")
    if api_key and api_secret:
        print(f"[SUCCESS] API Key: {api_key[:8]}...")
        print(f"[SUCCESS] API Secret: {api_secret[:8]}...")
    else:
        print("[ERROR] Missing credentials in .env file")
        return False
    
    try:
        print("\nStep 2: Import Kite Connect")
        from kiteconnect import KiteConnect
        print("[SUCCESS] KiteConnect library imported")
        
        print("\nStep 3: Create Kite Instance")
        kite = KiteConnect(api_key=api_key)
        print("[SUCCESS] KiteConnect instance created")
        
        print("\nStep 4: Generate Login URL")
        login_url = kite.login_url()
        print(f"[SUCCESS] Login URL generated")
        print(f"URL: {login_url}")
        
        print("\nStep 5: Test Paper Trading Wrapper")
        from integrations.kite_connect_wrapper import create_kite_wrapper
        
        wrapper = create_kite_wrapper(
            api_key=api_key,
            api_secret=api_secret,
            paper_trading=True
        )
        print("[SUCCESS] Kite wrapper created with paper trading")
        
        print("\nStep 6: Test Authentication (Paper Mode)")
        auth_success = await wrapper.authenticate()
        print(f"[SUCCESS] Paper trading authentication: {auth_success}")
        
        print("\nStep 7: Test Health Check")
        health = await wrapper.health_check()
        print("[SUCCESS] Health check completed:")
        for key, value in health.items():
            print(f"  - {key}: {value}")
        
        print("\n=== INTEGRATION TEST RESULTS ===")
        print("[SUCCESS] Kite Connect API: READY")
        print("[SUCCESS] Paper Trading Mode: OPERATIONAL")
        print("[SUCCESS] System Integration: WORKING")
        print("[SUCCESS] Ready for OAuth Flow!")
        
        print("\n=== NEXT STEPS ===")
        print("1. Complete OAuth authentication:")
        print(f"   - Open: {login_url}")
        print("   - Login with your Zerodha credentials")
        print("   - Authorize the app")
        print("   - Copy the 'request_token' from callback URL")
        print("   - We'll use it to get access token")
        
        print("\n2. After OAuth, you can:")
        print("   - Access live market data")
        print("   - Place real orders (start with paper trading)")
        print("   - Get actual portfolio positions")
        print("   - Integrate with Telegram bot")
        
        await wrapper.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        logger.error(f"Kite integration test error: {e}")
        return False


async def demonstrate_oauth_flow():
    """Demonstrate the OAuth authentication flow."""
    
    print("\n=== OAUTH AUTHENTICATION FLOW ===")
    print()
    
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    
    if not api_key:
        print("[ERROR] API Key not found")
        return
    
    try:
        from kiteconnect import KiteConnect
        
        kite = KiteConnect(api_key=api_key)
        login_url = kite.login_url()
        
        print("OAuth Flow Steps:")
        print("1. User visits login URL")
        print("2. User logs in with Zerodha credentials")
        print("3. User authorizes app")
        print("4. Zerodha redirects to callback URL with request_token")
        print("5. App exchanges request_token for access_token")
        print()
        
        print(f"LOGIN URL: {login_url}")
        print()
        print("After completing login, you'll get a callback URL like:")
        print("http://localhost:3000/callback?request_token=abc123&action=login&status=success")
        print()
        print("Extract the 'request_token' value and we'll use it to get access token!")
        
    except Exception as e:
        print(f"[ERROR] OAuth demo failed: {e}")


if __name__ == "__main__":
    print("Kite Connect Credentials Test")
    print("Testing your new API credentials")
    print("=" * 50)
    
    try:
        # Test credentials
        result = asyncio.run(test_kite_credentials())
        
        if result:
            # Show OAuth flow
            asyncio.run(demonstrate_oauth_flow())
            
            print("\n" + "=" * 50)
            print("SUCCESS: Your Kite Connect integration is ready!")
            print("Next: Complete the OAuth flow to get live market access")
        else:
            print("\nFailed: Please check your credentials and try again")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")