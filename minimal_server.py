"""
Ultra-minimal server using only Python built-ins
No external dependencies that require compilation
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks using built-in server."""
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        if path in ['/', '/health', '/status']:
            self.send_health_response()
        else:
            self.send_error(404)
    
    def send_health_response(self):
        """Send health check response."""
        health_data = {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "service": "Nifty/BankNifty Trading Bot",
            "platform": "Render.com",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "message": "Telegram bot server running successfully!",
            "configuration": {
                "bot_token_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
                "user_id_configured": bool(os.getenv("TELEGRAM_USER_ID")),
                "kite_api_configured": bool(os.getenv("KITE_API_KEY")),
                "paper_trading": os.getenv("ENABLE_PAPER_TRADING", "true") == "true"
            }
        }
        
        response = json.dumps(health_data, indent=2)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.client_address[0]} - {format % args}")

class MinimalTradingBotServer:
    """Ultra-minimal trading bot server."""
    
    def __init__(self):
        self.port = int(os.getenv("PORT", "10000"))
        self.running = False
        self.server = None
        
        # Load configuration
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.user_id = os.getenv("TELEGRAM_USER_ID")
        self.environment = os.getenv("ENVIRONMENT", "production")
        
        logger.info(f"🤖 Minimal Trading Bot Server Initializing")
        logger.info(f"📊 Environment: {self.environment}")
        logger.info(f"🌐 Port: {self.port}")
    
    def send_telegram_notification(self, message):
        """Send notification to Telegram using requests."""
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
            success = response.status_code == 200
            
            if success:
                logger.info("✅ Telegram notification sent successfully")
            else:
                logger.error(f"❌ Telegram notification failed: {response.status_code}")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def start_server(self):
        """Start the HTTP server."""
        try:
            logger.info("🚀 Starting Minimal Trading Bot Server...")
            
            # Create HTTP server
            self.server = HTTPServer(('0.0.0.0', self.port), HealthHandler)
            self.running = True
            
            logger.info(f"✅ Server started on port {self.port}")
            logger.info(f"🔗 Health check: http://localhost:{self.port}/health")
            
            # Send startup notification in background
            threading.Thread(target=self._send_startup_notification, daemon=True).start()
            
            # Start server (this blocks)
            self.server.serve_forever()
            
        except Exception as e:
            logger.error(f"❌ Server failed to start: {e}")
            raise
    
    def _send_startup_notification(self):
        """Send startup notification in background thread."""
        # Wait a moment for server to fully start
        time.sleep(2)
        
        startup_msg = f"""🚀 **Trading Bot Server Started on Render**

✅ **System Status**
• Server: Online and Running
• Platform: Render.com  
• Environment: {self.environment}
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 **Configuration**
• Bot Token: {'✅ Configured' if self.bot_token else '❌ Missing'}
• User ID: {'✅ Configured' if self.user_id else '❌ Missing'}
• Paper Trading: {os.getenv('ENABLE_PAPER_TRADING', 'true')}

🌐 **Health Endpoints**
• Status: /health
• Health Check: ✅ Active

Your sophisticated trading system is now running 24/7 in the cloud! 📱

Next step: Deploy AWS Lambda for trading execution."""

        self.send_telegram_notification(startup_msg)
    
    def shutdown(self):
        """Shutdown server."""
        logger.info("🛑 Shutting down server...")
        self.running = False
        if self.server:
            self.server.shutdown()

def main():
    """Main function."""
    try:
        server = MinimalTradingBotServer()
        server.start_server()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("🎯 Starting Ultra-Minimal Trading Bot Server")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    main()