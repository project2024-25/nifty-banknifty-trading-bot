"""
Simple Telegram Bot Server for Render Deployment
Minimal dependencies version for reliable cloud deployment
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from aiohttp import web
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleTradingBotServer:
    """Simple Telegram bot server with minimal dependencies."""
    
    def __init__(self):
        self.running = False
        self.health_status = "starting"
        
        # Load configuration
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.user_id = os.getenv("TELEGRAM_USER_ID")
        self.port = int(os.getenv("PORT", "10000"))
        self.environment = os.getenv("ENVIRONMENT", "production")
        
        logger.info(f"🤖 Initializing Simple Trading Bot Server")
        logger.info(f"📊 Environment: {self.environment}")
        logger.info(f"🌐 Port: {self.port}")
        
    async def health_check(self, request):
        """Health check endpoint for Render."""
        health_data = {
            "status": self.health_status,
            "timestamp": datetime.now().isoformat(),
            "service": "Nifty/BankNifty Trading Bot",
            "environment": self.environment,
            "bot_configured": bool(self.bot_token),
            "uptime": "running" if self.running else "starting"
        }
        
        status_code = 200 if self.health_status == "running" else 503
        return web.json_response(health_data, status=status_code)
    
    async def status_endpoint(self, request):
        """Detailed status endpoint."""
        status_data = {
            "service": "Nifty/BankNifty Trading Bot",
            "version": "1.0.0",
            "status": self.health_status,
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "environment": self.environment,
                "port": self.port,
                "bot_token_configured": bool(self.bot_token),
                "user_id_configured": bool(self.user_id)
            },
            "message": "Telegram bot server running successfully on Render!"
        }
        
        return web.json_response(status_data)
    
    async def send_telegram_message(self, message):
        """Send message to Telegram using simple HTTP request."""
        if not self.bot_token or not self.user_id:
            logger.warning("Telegram credentials not configured")
            return False
            
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.user_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def start_server(self):
        """Start the web server."""
        try:
            logger.info("🚀 Starting Simple Telegram Bot Server...")
            
            # Create web application
            app = web.Application()
            app.router.add_get('/health', self.health_check)
            app.router.add_get('/status', self.status_endpoint)
            app.router.add_get('/', self.status_endpoint)
            
            # Start server
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', self.port)
            await site.start()
            
            self.running = True
            self.health_status = "running"
            
            logger.info(f"✅ Server started successfully on port {self.port}")
            logger.info(f"🔗 Health check: http://localhost:{self.port}/health")
            
            # Send startup notification
            startup_msg = f"""🚀 **Trading Bot Server Started on Render**

✅ **System Status**
• Server: Online and Running  
• Environment: {self.environment}
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🌐 **Deployment Info**
• Platform: Render.com
• Health Check: ✅ Active
• Auto-restart: ✅ Enabled

Your sophisticated trading system is now running 24/7 in the cloud! 📱"""

            await self.send_telegram_message(startup_msg)
            
            # Keep server running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Server failed to start: {e}")
            self.health_status = "failed"
            raise
    
    def shutdown(self):
        """Graceful shutdown."""
        logger.info("🛑 Shutting down server...")
        self.running = False
        self.health_status = "shutting_down"

# Global server instance
server = None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}")
    if server:
        server.shutdown()

async def main():
    """Main function."""
    global server
    
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create and start server
        server = SimpleTradingBotServer()
        await server.start_server()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    logger.info("🎯 Starting Nifty/BankNifty Trading Bot on Render")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)