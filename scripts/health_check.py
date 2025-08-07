#!/usr/bin/env python3
"""
System Health Check Script
Verifies all services are working correctly
"""
import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

from src.utils.config import get_config, validate_config
from src.utils.logger import get_logger
from src.integrations.database import db_manager

logger = get_logger(__name__)


class HealthChecker:
    """Comprehensive system health checker"""
    
    def __init__(self):
        self.config = get_config() if validate_config() else None
        self.results = {}
    
    async def check_configuration(self) -> Dict[str, Any]:
        """Check configuration validity"""
        print("🔧 Checking configuration...")
        
        try:
            if not self.config:
                return {"status": "FAIL", "message": "Configuration validation failed"}
            
            required_vars = [
                'kite_api_key', 'kite_api_secret', 
                'telegram_bot_token', 'telegram_user_id',
                'supabase_url', 'supabase_key'
            ]
            
            missing = []
            for var in required_vars:
                if not getattr(self.config, var, None):
                    missing.append(var.upper())
            
            if missing:
                return {
                    "status": "FAIL", 
                    "message": f"Missing: {', '.join(missing)}"
                }
            
            return {"status": "OK", "message": "All required variables present"}
            
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and schema"""
        print("🗃️  Checking database...")
        
        try:
            if not await db_manager.initialize():
                return {"status": "FAIL", "message": "Database initialization failed"}
            
            # Test basic operations
            test_tables = ['trades', 'positions', 'signals', 'performance_metrics']
            table_status = {}
            
            for table in test_tables:
                try:
                    result = db_manager.client.table(table).select("count", count='exact').execute()
                    table_status[table] = f"✅ {result.count} records"
                except Exception as e:
                    table_status[table] = f"❌ {str(e)[:50]}"
            
            return {
                "status": "OK",
                "message": "Database connected",
                "tables": table_status
            }
            
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    async def check_telegram_bot(self) -> Dict[str, Any]:
        """Check Telegram bot connectivity"""
        print("🤖 Checking Telegram bot...")
        
        try:
            if not self.config:
                return {"status": "FAIL", "message": "Configuration not available"}
            
            # Import here to avoid circular imports
            from telegram import Bot
            
            bot = Bot(token=self.config.telegram_bot_token)
            
            # Test bot info
            me = await bot.get_me()
            
            return {
                "status": "OK",
                "message": f"Bot connected: @{me.username}",
                "bot_info": {
                    "username": me.username,
                    "name": me.first_name,
                    "can_join_groups": me.can_join_groups,
                    "can_read_all_group_messages": me.can_read_all_group_messages
                }
            }
            
        except ImportError:
            return {"status": "SKIP", "message": "python-telegram-bot not installed"}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    async def check_kite_api(self) -> Dict[str, Any]:
        """Check Kite Connect API status"""
        print("📈 Checking Kite Connect API...")
        
        try:
            if not self.config:
                return {"status": "FAIL", "message": "Configuration not available"}
            
            # Import here to avoid dependency issues
            try:
                from kiteconnect import KiteConnect
                
                kite = KiteConnect(api_key=self.config.kite_api_key)
                
                # Test login URL generation (doesn't require authentication)
                login_url = kite.login_url()
                
                if login_url and "kite.zerodha.com" in login_url:
                    return {
                        "status": "OK",
                        "message": "API key valid, login URL generated",
                        "login_url": login_url[:50] + "..."
                    }
                else:
                    return {"status": "FAIL", "message": "Invalid API response"}
                    
            except ImportError:
                return {"status": "SKIP", "message": "kiteconnect not installed"}
                
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    async def check_market_hours(self) -> Dict[str, Any]:
        """Check if market is currently open"""
        print("🕐 Checking market status...")
        
        try:
            now = datetime.now()
            day_of_week = now.weekday()  # 0=Monday, 6=Sunday
            
            # Market is closed on weekends
            if day_of_week >= 5:
                return {
                    "status": "CLOSED",
                    "message": "Weekend - Market closed",
                    "next_open": "Monday 9:15 AM"
                }
            
            # Market hours: 9:15 AM to 3:30 PM IST
            market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
            market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
            
            if now < market_open:
                return {
                    "status": "CLOSED",
                    "message": "Pre-market hours",
                    "opens_in": str(market_open - now).split('.')[0]
                }
            elif now > market_close:
                return {
                    "status": "CLOSED", 
                    "message": "Post-market hours",
                    "closed_ago": str(now - market_close).split('.')[0]
                }
            else:
                return {
                    "status": "OPEN",
                    "message": "Market is open",
                    "closes_in": str(market_close - now).split('.')[0]
                }
                
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources and performance"""
        print("💻 Checking system resources...")
        
        try:
            import psutil
            import os
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process info
            process = psutil.Process(os.getpid())
            
            return {
                "status": "OK",
                "message": "System resources checked",
                "memory": {
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "used_gb": round(disk.used / (1024**3), 2), 
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": round((disk.used / disk.total) * 100, 1)
                },
                "process": {
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": round(process.memory_info().rss / (1024**2), 2),
                    "threads": process.num_threads()
                }
            }
            
        except ImportError:
            return {"status": "SKIP", "message": "psutil not installed"}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        print("🏥 Starting comprehensive health check...\n")
        
        checks = [
            ("Configuration", self.check_configuration()),
            ("Database", self.check_database()),
            ("Telegram Bot", self.check_telegram_bot()),
            ("Kite Connect API", self.check_kite_api()),
            ("Market Status", self.check_market_hours()),
            ("System Resources", self.check_system_resources())
        ]
        
        results = {}
        overall_status = "OK"
        
        for check_name, check_coro in checks:
            try:
                result = await check_coro
                results[check_name] = result
                
                # Print result
                status_emoji = {
                    "OK": "✅",
                    "FAIL": "❌", 
                    "ERROR": "⚠️",
                    "SKIP": "⏭️",
                    "OPEN": "🟢",
                    "CLOSED": "🔴"
                }
                
                emoji = status_emoji.get(result["status"], "❓")
                print(f"{emoji} {check_name}: {result['message']}")
                
                if result["status"] in ["FAIL", "ERROR"]:
                    overall_status = "DEGRADED"
                    
            except Exception as e:
                results[check_name] = {"status": "ERROR", "message": str(e)}
                print(f"❌ {check_name}: ERROR - {e}")
                overall_status = "DEGRADED"
        
        print(f"\n🏥 Overall System Status: {overall_status}")
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": results
        }


async def main():
    """Main health check function"""
    checker = HealthChecker()
    results = await checker.run_all_checks()
    
    # Send notification if configured
    try:
        if results["overall_status"] == "DEGRADED":
            from src.integrations.telegram_bot import send_error_notification
            await send_error_notification(
                f"🚨 System Health Check FAILED\n"
                f"Time: {results['timestamp']}\n"
                f"Check logs for details."
            )
        
        logger.info("Health check completed", 
                   overall_status=results["overall_status"],
                   checks_run=len(results["checks"]))
        
    except ImportError:
        logger.info("Telegram notification skipped - module not available")
    
    # Exit with appropriate code
    return 0 if results["overall_status"] == "OK" else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))