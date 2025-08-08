"""
Telegram Bot Server for Railway/Render Deployment

This server runs the Telegram bot 24/7 in the cloud, providing
mobile control interface for the trading system.
"""

import asyncio
import logging
import os
import sys
import signal
from datetime import datetime
from typing import Optional
import uvloop  # For better async performance

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import bot components
try:
    from integrations.telegram_trading_interface import create_advanced_telegram_bot
    from integrations.kite_connect_wrapper import create_kite_wrapper
except ImportError as e:
    logging.error(f"Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('telegram_bot.log')
    ]
)

logger = logging.getLogger(__name__)

class TradingBotServer:
    """
    24/7 Telegram bot server for trading system control.
    
    Provides mobile interface for:
    - Real-time portfolio monitoring
    - Trade execution controls  
    - Emergency stop functionality
    - Performance analytics
    - System health monitoring
    """
    
    def __init__(self):
        self.bot = None
        self.kite_wrapper = None
        self.running = False
        self.health_status = "starting"
        
        # Load configuration from environment
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.user_id = int(os.getenv("TELEGRAM_USER_ID", "0"))
        self.kite_api_key = os.getenv("KITE_API_KEY")
        self.kite_api_secret = os.getenv("KITE_API_SECRET")
        self.kite_access_token = os.getenv("KITE_ACCESS_TOKEN")
        
        # Server configuration
        self.port = int(os.getenv("PORT", "8000"))
        self.environment = os.getenv("ENVIRONMENT", "production")
        
    async def initialize(self):
        """Initialize all components."""
        
        try:
            logger.info("🤖 Initializing Trading Bot Server...")
            
            # Validate configuration
            if not all([self.bot_token, self.user_id, self.kite_api_key, self.kite_api_secret]):
                raise ValueError("Missing required environment variables")
            
            # Initialize Kite Connect wrapper
            logger.info("🔗 Initializing Kite Connect wrapper...")
            self.kite_wrapper = create_kite_wrapper(
                api_key=self.kite_api_key,
                api_secret=self.kite_api_secret,
                access_token=self.kite_access_token,
                paper_trading=os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true"
            )
            
            auth_success = await self.kite_wrapper.authenticate()
            logger.info(f"🔐 Kite authentication: {'Success' if auth_success else 'Failed'}")
            
            # Initialize Telegram bot
            logger.info("📱 Initializing Telegram bot...")
            self.bot = create_advanced_telegram_bot(self.bot_token, self.user_id)
            await self.bot.initialize()
            
            logger.info("✅ All components initialized successfully")
            self.health_status = "healthy"
            
            # Send startup notification
            await self.send_startup_notification()
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            self.health_status = "unhealthy"
            raise
    
    async def start_server(self):
        """Start the bot server."""
        
        try:
            logger.info("🚀 Starting Telegram Bot Server...")
            logger.info(f"📊 Environment: {self.environment}")
            logger.info(f"🌐 Port: {self.port}")
            logger.info(f"👤 Authorized User: {self.user_id}")
            
            self.running = True
            self.health_status = "running"
            
            # Start health check server
            health_task = asyncio.create_task(self.start_health_server())
            
            # Start bot
            bot_task = asyncio.create_task(self.bot.run())
            
            # Wait for tasks
            await asyncio.gather(health_task, bot_task)
            
        except Exception as e:
            logger.error(f"❌ Server start failed: {e}")
            self.health_status = "failed"
            raise
    
    async def start_health_server(self):
        """Start HTTP health check server for Railway/Render."""
        
        try:
            from aiohttp import web, web_request
            
            async def health_check(request: web_request.Request):
                """Health check endpoint."""
                
                health_data = {
                    "status": self.health_status,
                    "timestamp": datetime.now().isoformat(),
                    "bot_running": self.running,
                    "environment": self.environment,
                    "user_id": self.user_id,
                    "kite_authenticated": bool(self.kite_wrapper and self.kite_wrapper.authenticated),
                    "paper_trading": os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true"
                }
                
                status_code = 200 if self.health_status == "running" else 503
                return web.json_response(health_data, status=status_code)
            
            async def status_endpoint(request: web_request.Request):
                """Detailed status endpoint."""
                
                status_data = {
                    "service": "Nifty/BankNifty Trading Bot",
                    "version": "1.0.0",
                    "status": self.health_status,
                    "uptime": "N/A",  # Could calculate uptime
                    "components": {
                        "telegram_bot": bool(self.bot),
                        "kite_connect": bool(self.kite_wrapper),
                        "authentication": bool(self.kite_wrapper and self.kite_wrapper.authenticated)
                    },
                    "configuration": {
                        "environment": self.environment,
                        "paper_trading": os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true",
                        "authorized_user": self.user_id
                    }
                }
                
                return web.json_response(status_data)
            
            # Create web application
            app = web.Application()
            app.router.add_get('/health', health_check)
            app.router.add_get('/status', status_endpoint)
            app.router.add_get('/', status_endpoint)  # Root endpoint
            
            # Start server
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', self.port)
            await site.start()
            
            logger.info(f"🌐 Health server started on port {self.port}")
            logger.info(f"🔗 Health check: http://localhost:{self.port}/health")
            
            # Keep server running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Health server failed: {e}")
    
    async def send_startup_notification(self):
        """Send startup notification to user."""
        
        try:
            startup_message = f"""
🚀 **Trading Bot Server Started**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **System Status**
• Server: Online and Running
• Environment: {self.environment.title()}
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 **Connections**
• Kite Connect: {"✅ Authenticated" if self.kite_wrapper and self.kite_wrapper.authenticated else "❌ Failed"}
• Telegram Bot: ✅ Active
• Mode: {"📋 Paper Trading" if os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true" else "💰 Live Trading"}

🎯 **Available Commands**
• /status - Portfolio status
• /positions - Open positions  
• /analysis - Market analysis
• /help - All commands

Your sophisticated trading bot is now accessible 24/7! 📱
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            
            if self.bot:
                await self.bot.send_notification(startup_message)
                
        except Exception as e:
            logger.error(f"Failed to send startup notification: {e}")
    
    async def shutdown(self):
        """Graceful shutdown."""
        
        logger.info("🛑 Shutting down bot server...")
        
        self.running = False
        self.health_status = "shutting_down"
        
        try:
            # Send shutdown notification
            if self.bot:
                await self.bot.send_notification(
                    "🛑 **Trading Bot Server Shutting Down**\n\n"
                    "The server is being shut down. It will restart automatically.\n"
                    "Your trading positions remain safe."
                )
                
                await self.bot.stop()
            
            # Close Kite wrapper
            if self.kite_wrapper:
                await self.kite_wrapper.close()
            
            logger.info("✅ Shutdown completed gracefully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global server instance
server = None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, shutting down...")
    if server:
        asyncio.create_task(server.shutdown())

async def main():
    """Main server function."""
    
    global server
    
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create and start server
        server = TradingBotServer()
        await server.initialize()
        await server.start_server()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        if server:
            await server.shutdown()

if __name__ == "__main__":
    # Use uvloop for better performance
    if sys.platform != 'win32':
        uvloop.install()
    
    logger.info("🎯 Starting Nifty/BankNifty Trading Bot Server")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)