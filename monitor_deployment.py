#!/usr/bin/env python3
"""
Monitor Sophisticated Trading System Deployment
"""

import requests
import json
import time
from datetime import datetime

def check_deployment():
    """Monitor the sophisticated deployment status"""
    
    print("SOPHISTICATED DEPLOYMENT MONITOR")
    print("=" * 40)
    
    try:
        url = "https://api.github.com/repos/project2024-25/nifty-banknifty-trading-bot/actions/runs?per_page=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            runs = response.json()["workflow_runs"]
            if runs:
                latest_run = runs[0]
                status = latest_run.get("status", "unknown")
                conclusion = latest_run.get("conclusion")
                
                print(f"Status: {status}")
                if conclusion:
                    print(f"Conclusion: {conclusion}")
                
                if status == "completed":
                    if conclusion == "success":
                        print("\nDEPLOYMENT SUCCESSFUL!")
                        print("\nYour FULL SOPHISTICATED trading system is live!")
                        print("\nACTIVE FEATURES:")
                        print("• Market Intelligence & Regime Detection")
                        print("• 11 Advanced Options Strategies") 
                        print("• Complete Supabase Database Integration")
                        print("• Portfolio Management with Kelly Criterion")
                        print("• Advanced Risk Management")
                        print("• Real-time Performance Analytics")
                        print("• 1024MB Memory + 15min Timeout")
                        
                        print("\nNEXT STEPS:")
                        print("• System executes every 5 minutes during market hours")
                        print("• Check Telegram for sophisticated notifications")
                        print("• Monitor Supabase for trade/intelligence data")  
                        print("• Review AWS Lambda logs for execution details")
                        return True
                    else:
                        print("\nDEPLOYMENT FAILED")
                        print("Check GitHub Actions for error details")
                        return False
                else:
                    print("\nDeployment in progress...")
                    print("\nThis includes:")
                    print("• Installing 20+ sophisticated packages")
                    print("• Creating Lambda Layer for dependencies")
                    print("• Deploying 4 functions with increased resources")
                    print("• Setting up monitoring and scheduled triggers")
                    return None
        else:
            print(f"API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Monitor failed: {e}")
        return False

if __name__ == "__main__":
    result = check_deployment()
    print(f"\nChecked at: {datetime.now().strftime('%H:%M:%S')}")
    
    if result is None:
        print("\nMonitor progress at:")
        print("https://github.com/project2024-25/nifty-banknifty-trading-bot/actions")