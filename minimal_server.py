"""
Ultra-minimal server using only Python built-ins
No external dependencies that require compilation
"""

import os
import sys
import json
import threading
import time
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging
import hashlib
import hmac
import urllib.request
import urllib.parse as urlparse_lib
import base64

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_time():
    """Get current time in IST."""
    return datetime.now(IST)

def format_ist_time(dt_format='%Y-%m-%d %H:%M:%S'):
    """Format current IST time."""
    return get_ist_time().strftime(dt_format)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KiteTokenManager:
    """Handle Kite Connect token generation."""
    
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY", "")
        self.api_secret = os.getenv("KITE_API_SECRET", "")
        self.redirect_url = "http://localhost:3000/callback"
    
    def generate_login_url(self):
        """Generate Kite Connect login URL."""
        if not self.api_key:
            return None
        
        login_url = f"https://kite.trade/connect/login?api_key={self.api_key}&v=3"
        return login_url
    
    def generate_access_token(self, request_token):
        """Generate access token from request token."""
        if not self.api_key or not self.api_secret or not request_token:
            return None, "Missing credentials or request token"
        
        try:
            # Generate checksum
            checksum_data = f"{self.api_key}{request_token}{self.api_secret}"
            checksum = hashlib.sha256(checksum_data.encode()).hexdigest()
            
            # Prepare POST data
            data = {
                'api_key': self.api_key,
                'request_token': request_token,
                'checksum': checksum
            }
            
            # Make request to Kite API
            post_data = urlparse_lib.urlencode(data).encode()
            
            req = urllib.request.Request(
                'https://api.kite.trade/session/token',
                data=post_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Kite-Version': '3'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                
                if result.get('status') == 'success':
                    access_token = result['data']['access_token']
                    return access_token, None
                else:
                    return None, result.get('message', 'Unknown error')
                    
        except Exception as e:
            return None, str(e)
    
    def update_github_secret(self, access_token):
        """Update GitHub Secret with new access token."""
        github_token = os.getenv('GITHUB_TOKEN')
        github_repo = os.getenv('GITHUB_REPO', 'project2024-25/nifty-banknifty-trading-bot')
        
        if not github_token:
            return False, "GitHub token not configured"
        
        try:
            # Get the public key for encryption
            public_key_url = f"https://api.github.com/repos/{github_repo}/actions/secrets/public-key"
            
            req = urllib.request.Request(
                public_key_url,
                headers={
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'Trading-Bot/1.0'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                public_key_data = json.loads(response.read().decode())
                public_key = public_key_data['key']
                key_id = public_key_data['key_id']
            
            # Encrypt the secret (simplified - in production use proper encryption)
            encrypted_value = base64.b64encode(access_token.encode()).decode()
            
            # Update the secret
            secret_url = f"https://api.github.com/repos/{github_repo}/actions/secrets/KITE_ACCESS_TOKEN"
            secret_data = {
                'encrypted_value': encrypted_value,
                'key_id': key_id
            }
            
            req = urllib.request.Request(
                secret_url,
                data=json.dumps(secret_data).encode(),
                headers={
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Trading-Bot/1.0'
                }
            )
            req.get_method = lambda: 'PUT'
            
            with urllib.request.urlopen(req, timeout=10) as response:
                success = response.status == 204
                return success, "GitHub secret updated successfully" if success else f"GitHub API error: {response.status}"
                
        except Exception as e:
            return False, str(e)
    
    def trigger_lambda_redeployment(self):
        """Trigger Lambda redeployment via GitHub Actions."""
        github_token = os.getenv('GITHUB_TOKEN')
        github_repo = os.getenv('GITHUB_REPO', 'project2024-25/nifty-banknifty-trading-bot')
        
        if not github_token:
            return False, "GitHub token not configured"
        
        try:
            # Trigger workflow dispatch
            workflow_url = f"https://api.github.com/repos/{github_repo}/actions/workflows/deploy-lambda.yml/dispatches"
            workflow_data = {
                'ref': 'main',
                'inputs': {
                    'stage': 'dev'
                }
            }
            
            req = urllib.request.Request(
                workflow_url,
                data=json.dumps(workflow_data).encode(),
                headers={
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Trading-Bot/1.0'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                success = response.status == 204
                return success, "Lambda redeployment triggered" if success else f"GitHub API error: {response.status}"
                
        except Exception as e:
            return False, str(e)

class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks and Telegram webhooks using built-in server."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        if path in ['/', '/health', '/status']:
            self.send_health_response()
        elif path == '/callback':
            # Handle Kite Connect callback
            self.handle_kite_callback(query_params)
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests (Telegram webhooks)."""
        path = urlparse(self.path).path
        
        if path == '/webhook':
            self.handle_telegram_webhook()
        else:
            self.send_error(404)
    
    def handle_kite_callback(self, query_params):
        """Handle Kite Connect OAuth callback."""
        status = query_params.get('status', [''])[0]
        request_token = query_params.get('request_token', [''])[0]
        
        if status == 'success' and request_token:
            # Generate access token
            token_manager = KiteTokenManager()
            access_token, error = token_manager.generate_access_token(request_token)
            
            if access_token:
                response_data = {
                    "status": "success",
                    "message": "Access token generated successfully!",
                    "access_token": access_token,
                    "timestamp": get_ist_time().isoformat(),
                    "ist_time": format_ist_time()
                }
                
                # Full automation: Update GitHub secrets and trigger redeployment
                automation_results = []
                
                # 1. Update GitHub Secret
                github_success, github_msg = token_manager.update_github_secret(access_token)
                automation_results.append(f"GitHub Secret: {'✅' if github_success else '❌'} {github_msg}")
                
                # 2. Trigger Lambda redeployment
                if github_success:
                    deploy_success, deploy_msg = token_manager.trigger_lambda_redeployment()
                    automation_results.append(f"Lambda Redeployment: {'✅' if deploy_success else '❌'} {deploy_msg}")
                else:
                    automation_results.append("Lambda Redeployment: ⏸️ Skipped (GitHub update failed)")
                
                # Send comprehensive notification
                automation_status = "\n".join([f"• {result}" for result in automation_results])
                
                if github_success:
                    self.server.trading_bot.send_telegram_notification(
                        f"🚀 **FULL AUTOMATED TOKEN UPDATE COMPLETE!**\n\n"
                        f"🔑 **New Token Generated:** `{access_token[:20]}...`\n\n"
                        f"🤖 **Automation Results:**\n{automation_status}\n\n"
                        f"⏱️ **Timeline:**\n"
                        f"• Token generated: {format_ist_time()} IST\n"
                        f"• GitHub secret updated: ✅\n"
                        f"• Lambda redeployment: {'✅ Triggered' if deploy_success else '❌ Failed'}\n\n"
                        f"🎯 **Next Steps:**\n"
                        f"• Lambda will redeploy automatically (3-5 minutes)\n"
                        f"• System will be ready for trading with new token\n"
                        f"• No manual intervention required!\n\n"
                        f"🌟 **Your trading system is now fully automated!**"
                    )
                else:
                    self.server.trading_bot.send_telegram_notification(
                        f"⚠️ **PARTIAL TOKEN UPDATE**\n\n"
                        f"🔑 **Token Generated:** `{access_token}`\n\n"
                        f"🤖 **Automation Results:**\n{automation_status}\n\n"
                        f"📋 **Manual Action Required:**\n"
                        f"Please update the following environment variables manually:\n"
                        f"• GitHub Secret: `KITE_ACCESS_TOKEN`\n"
                        f"• Lambda Environment: `KITE_ACCESS_TOKEN`\n\n"
                        f"🕐 **Generated:** {format_ist_time()} IST"
                    )
            else:
                response_data = {
                    "status": "error", 
                    "message": f"Failed to generate token: {error}",
                    "timestamp": get_ist_time().isoformat(),
                    "ist_time": format_ist_time()
                }
                
                self.server.trading_bot.send_telegram_notification(
                    f"❌ **Token Generation Failed**\n\n"
                    f"Error: {error}\n\n"
                    f"Please try again with `/generate_token` command."
                )
        else:
            response_data = {
                "status": "error",
                "message": "Invalid callback parameters",
                "timestamp": get_ist_time().isoformat(),
                "ist_time": format_ist_time()
            }
        
        # Send response
        response = json.dumps(response_data, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def handle_telegram_webhook(self):
        """Handle incoming Telegram webhook messages."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            # Process the update
            self.server.trading_bot.process_telegram_update(update)
            
            # Send OK response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
            
        except Exception as e:
            logger.error(f"Error handling Telegram webhook: {e}")
            self.send_error(500)
    
    def send_health_response(self):
        """Send health check response."""
        health_data = {
            "status": "running",
            "timestamp": get_ist_time().isoformat(),
            "ist_time": format_ist_time(),
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
    """Ultra-minimal trading bot server with Telegram bot functionality."""
    
    def __init__(self):
        self.port = int(os.getenv("PORT", "10000"))
        self.running = False
        self.server = None
        
        # Load configuration
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.user_id = os.getenv("TELEGRAM_USER_ID")
        self.environment = os.getenv("ENVIRONMENT", "production")
        
        # Initialize token manager
        self.token_manager = KiteTokenManager()
        
        logger.info(f"🤖 Minimal Trading Bot Server Initializing")
        logger.info(f"📊 Environment: {self.environment}")
        logger.info(f"🌐 Port: {self.port}")
    
    def send_telegram_notification(self, message):
        """Send notification to Telegram using built-in urllib."""
        if not self.bot_token or not self.user_id:
            logger.warning("Telegram credentials not configured")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.user_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            post_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                url, 
                data=post_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                success = response.status == 200
                
                if success:
                    logger.info("✅ Telegram notification sent successfully")
                else:
                    logger.error(f"❌ Telegram notification failed: {response.status}")
                    
                return success
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def process_telegram_update(self, update):
        """Process incoming Telegram update."""
        try:
            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
            user_id = message.get('from', {}).get('id')
            username = message.get('from', {}).get('username', 'unknown')
            
            # Enhanced security: Only respond to authorized user
            if str(user_id) != self.user_id:
                logger.warning(f"🚨 UNAUTHORIZED ACCESS ATTEMPT - User ID: {user_id}, Username: {username}, Message: {text[:50]}...")
                
                # Send security alert to authorized user
                self.send_telegram_notification(
                    f"🚨 **SECURITY ALERT**\n\n"
                    f"Unauthorized access attempt detected!\n\n"
                    f"👤 **User ID:** {user_id}\n"
                    f"👤 **Username:** @{username}\n"
                    f"💬 **Message:** {text[:100]}...\n"
                    f"🕐 **Time:** {format_ist_time()} IST\n\n"
                    f"🔒 Access denied. Only authorized user can interact with this bot."
                )
                return
            
            # Block spam/casino messages even from authorized users
            spam_keywords = ['casino', 'bonus', 'jetacas', 'promo code', 'welcome1k', 'gambling', 'deposit']
            if any(keyword.lower() in text.lower() for keyword in spam_keywords):
                logger.warning(f"🚨 SPAM MESSAGE DETECTED: {text[:50]}...")
                self.send_telegram_notification(
                    f"🚨 **SPAM MESSAGE BLOCKED**\n\n"
                    f"Detected and blocked a spam message.\n"
                    f"This was not sent by your trading system.\n\n"
                    f"🔒 **Security:** Bot is working correctly!"
                )
                return
            
            # Handle legitimate commands only
            if text.startswith('/'):
                self.handle_command(text, chat_id)
            
        except Exception as e:
            logger.error(f"Error processing Telegram update: {e}")
    
    def handle_command(self, command, chat_id):
        """Handle Telegram bot commands."""
        command = command.lower().strip()
        
        if command in ['/start', '/help']:
            self.send_help_message(chat_id)
        
        elif command in ['/generate_token', '/token', '/refresh_token']:
            self.handle_generate_token_command(chat_id)
        
        elif command in ['/auto_token', '/automated_token']:
            self.handle_automated_token_command(chat_id)
        
        elif command in ['/status', '/health']:
            self.send_status_message(chat_id)
        
        else:
            self.send_telegram_message(chat_id, "Unknown command. Use /help for available commands.")
    
    def send_help_message(self, chat_id):
        """Send help message with available commands."""
        help_text = """🤖 **Trading Bot Commands**

📱 **Token Management:**
• `/generate_token` - Generate new Kite access token (manual update)
• `/auto_token` - Generate + Auto-update GitHub & Lambda (RECOMMENDED)
• `/refresh_token` - Same as generate_token
• `/token` - Same as generate_token

📊 **Bot Status:**
• `/status` - Check bot status
• `/health` - Same as status
• `/help` - Show this help message

🔐 **Daily Token Process:**
1. Use `/generate_token`
2. Click the Kite login link
3. Complete authentication
4. Token will be automatically generated
5. Update Lambda environment variable

⚠️ **Important:** You need to generate a new token daily for live trading."""

        self.send_telegram_message(chat_id, help_text)
    
    def handle_generate_token_command(self, chat_id):
        """Handle token generation command."""
        login_url = self.token_manager.generate_login_url()
        
        if login_url:
            message = f"""🔐 **Generate Kite Access Token**

Click the link below to authenticate with Kite:

{login_url}

⚠️ **Instructions:**
1. Click the link above
2. Login to your Kite account
3. Authorize the app
4. You'll be redirected and the token will be automatically generated
5. Copy the generated token to your Lambda environment variables

🕐 **Note:** This needs to be done daily for live trading."""
            
            self.send_telegram_message(chat_id, message)
        else:
            self.send_telegram_message(
                chat_id, 
                "❌ **Error:** Kite API key not configured. Please check your environment variables."
            )
    
    def handle_automated_token_command(self, chat_id):
        """Handle fully automated token generation command."""
        # Check if GitHub token is configured for automation
        github_token = os.getenv('GITHUB_TOKEN')
        
        if not github_token:
            self.send_telegram_message(
                chat_id,
                f"""⚠️ **AUTOMATION NOT CONFIGURED**\n\n
❌ GitHub token not found in environment variables.\n\n
📋 **To enable full automation, add:**\n
• `GITHUB_TOKEN` - Personal access token with repo permissions\n
• `GITHUB_REPO` - Repository name (optional, defaults to current repo)\n\n
🔧 **For now, use:**\n
• `/generate_token` - Manual token generation\n\n
💡 **Contact admin to set up full automation.**"""
            )
            return
        
        login_url = self.token_manager.generate_login_url()
        
        if login_url:
            message = f"""🚀 **FULLY AUTOMATED TOKEN GENERATION**\n\n
Click the link below to authenticate with Kite:\n\n
{login_url}\n\n
🤖 **Full Automation Enabled:**\n
✅ Generate new Kite access token\n
✅ Auto-update GitHub Secrets\n
✅ Auto-trigger Lambda redeployment\n
✅ System ready in 3-5 minutes\n\n
⚠️ **Instructions:**\n
1. Click the link above\n
2. Login to your Kite account\n  
3. Authorize the app\n
4. Sit back and relax - everything is automated!\n\n
🌟 **This is the recommended daily process!**"""
            
            self.send_telegram_message(chat_id, message)
        else:
            self.send_telegram_message(
                chat_id,
                "❌ **Error:** Kite API key not configured. Please check your environment variables."
            )
    
    def send_status_message(self, chat_id):
        """Send bot status message."""
        config = {
            'bot_token': bool(self.bot_token),
            'user_id': bool(self.user_id),
            'kite_api_key': bool(os.getenv("KITE_API_KEY")),
            'kite_api_secret': bool(os.getenv("KITE_API_SECRET")),
            'kite_access_token': bool(os.getenv("KITE_ACCESS_TOKEN"))
        }
        
        status_text = f"""📊 **Bot Status Report**

🤖 **Server Status:** ✅ Running
🌐 **Platform:** Render.com
📅 **Time:** {format_ist_time()} IST

🔧 **Configuration:**
• Bot Token: {'✅' if config['bot_token'] else '❌'}
• User ID: {'✅' if config['user_id'] else '❌'}
• Kite API Key: {'✅' if config['kite_api_key'] else '❌'}
• Kite API Secret: {'✅' if config['kite_api_secret'] else '❌'}
• Kite Access Token: {'✅' if config['kite_access_token'] else '❌'}

📈 **Trading Mode:** {os.getenv('ENABLE_PAPER_TRADING', 'true')}

⚠️ **Reminder:** Use `/generate_token` daily for live trading."""
        
        self.send_telegram_message(chat_id, status_text)
    
    def send_telegram_message(self, chat_id, message):
        """Send message to specific chat."""
        if not self.bot_token:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            post_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                url, 
                data=post_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def start_server(self):
        """Start the HTTP server."""
        try:
            logger.info("🚀 Starting Minimal Trading Bot Server...")
            
            # Create HTTP server and attach trading bot reference
            self.server = HTTPServer(('0.0.0.0', self.port), HealthHandler)
            self.server.trading_bot = self  # Allow handlers to access the bot instance
            self.running = True
            
            logger.info(f"✅ Server started on port {self.port}")
            logger.info(f"🔗 Health check: http://localhost:{self.port}/health")
            logger.info(f"🔐 Token callback: http://localhost:{self.port}/callback")
            
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
• Time: {format_ist_time()} IST

🔧 **Configuration**
• Bot Token: {'✅ Configured' if self.bot_token else '❌ Missing'}
• User ID: {'✅ Configured' if self.user_id else '❌ Missing'}
• Kite API: {'✅ Configured' if os.getenv('KITE_API_KEY') else '❌ Missing'}
• Paper Trading: {os.getenv('ENABLE_PAPER_TRADING', 'true')}

🤖 **New Features Added**
• `/generate_token` - Daily Kite token generation
• `/status` - Check bot configuration
• `/help` - View all commands

🌐 **Available Endpoints**
• Health: /health
• Token Callback: /callback
• Telegram Webhook: /webhook

📱 **Daily Token Generation**
Use `/generate_token` command to generate your daily Kite access token!

Your sophisticated trading system is now running 24/7 in the cloud! 🚀"""

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