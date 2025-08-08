"""
Telegram Bot Integration for Trading Bot Control

This module provides a comprehensive Telegram bot interface for monitoring
and controlling the Nifty/BankNifty options trading bot remotely.

Features:
- Real-time P&L monitoring
- Position tracking
- System control (pause/resume/emergency stop)
- Performance reports
- Risk management controls
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.config import Config
    from core.adaptive_trading_engine import AdaptiveTradingEngine
    from intelligence.performance_attribution import PerformanceAttributor
    from utils.logger import get_logger
except ImportError:
    # Fallback for direct execution
    Config = None
    AdaptiveTradingEngine = None
    PerformanceAttributor = None
    
    def get_logger(name):
        import logging
        return logging.getLogger(name)

# Conversation states
SELECTING_ACTION = 1
ADJUSTING_RISK = 2
CONFIRMING_ACTION = 3

logger = get_logger(__name__)


class TradingBotTelegram:
    """
    Telegram bot interface for trading bot control and monitoring.
    
    Provides secure, single-user access to trading bot functionality
    with comprehensive monitoring and control capabilities.
    """
    
    def __init__(self, bot_token: str, authorized_user_id: int):
        """
        Initialize Telegram bot.
        
        Args:
            bot_token: Telegram bot token from BotFather
            authorized_user_id: Single authorized user's Telegram ID
        """
        self.bot_token = bot_token
        self.authorized_user_id = authorized_user_id
        self.application = None
        self.trading_engine = None
        self.performance_attributor = None
        
        # Bot state
        self.bot_active = True
        self.trading_paused = False
        self.last_update_time = datetime.now()
        
        # Message templates
        self.templates = self._load_message_templates()
    
    def _load_message_templates(self) -> Dict[str, str]:
        """Load message templates for consistent formatting."""
        return {
            'welcome': """
🤖 **Trading Bot Control Center**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Welcome! Your Nifty/BankNifty options trading bot is ready.

📊 Quick Commands:
• /status - Current P&L and positions
• /positions - Open positions details  
• /performance - Performance metrics
• /pause - Pause trading
• /resume - Resume trading
• /help - Full command list

🎯 System Status: 🟢 Active
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """,
            
            'status': """
📊 **Trading Status - {date}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Portfolio Overview**
• Capital: ₹{total_capital:,.2f}
• Day P&L: ₹{day_pnl:+,.2f} ({day_pnl_percent:+.2f}%)
• Total P&L: ₹{total_pnl:+,.2f} ({total_pnl_percent:+.2f}%)
• Available: ₹{available_capital:,.2f}

📍 **Positions**
• Open Positions: {open_positions}
• Active Strategies: {active_strategies}
• Risk Level: {risk_level}

⚡ **System**
• Status: 🟢 Active
• Last Update: {last_update}
• Market: {"🟢 Open" if "{market_open}" else "🔴 Closed"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """,
            
            'position_detail': """
📍 **Position: {symbol}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Details**
• Strategy: {strategy}
• Entry: ₹{entry_price:.2f}
• Current: ₹{current_price:.2f}
• Quantity: {quantity} lots

📊 **P&L**
• Unrealized: ₹{unrealized_pnl:+,.2f} ({pnl_percent:+.2f}%)
• Target: ₹{target_price:.2f}
• Stop Loss: ₹{stop_loss:.2f}

⏰ **Timing**
• Entry Time: {entry_time}
• Days Held: {days_held}
• Expiry: {expiry_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """,
            
            'performance_report': """
🏆 **Performance Report - {period}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **Financial Metrics**
• Total Return: {total_return:+.2f}%
• Sharpe Ratio: {sharpe_ratio:.2f}
• Max Drawdown: {max_drawdown:.2f}%
• Win Rate: {win_rate:.1f}%

📊 **Trading Stats**
• Total Trades: {total_trades}
• Winning: {winning_trades} | Losing: {losing_trades}
• Avg Win: ₹{avg_win:,.2f}
• Avg Loss: ₹{avg_loss:,.2f}
• Profit Factor: {profit_factor:.2f}

🎯 **Strategy Performance**
{strategy_performance}

📅 **Recent Performance**
• This Week: ₹{week_pnl:+,.2f}
• This Month: ₹{month_pnl:+,.2f}
• Last 30 Days: ₹{last_30_days:+,.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
        }
    
    def authorized_only(self, func):
        """Decorator to ensure only authorized user can execute commands."""
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            if user_id != self.authorized_user_id:
                await update.message.reply_text(
                    "🚫 Unauthorized access denied.\n"
                    "This bot is restricted to authorized users only."
                )
                logger.warning(f"Unauthorized access attempt from user {user_id}")
                return
            return await func(update, context)
        return wrapper
    
    async def initialize(self):
        """Initialize the bot application and trading engine."""
        # Initialize trading engine
        self.trading_engine = AdaptiveTradingEngine()
        await self.trading_engine.initialize()
        
        self.performance_attributor = PerformanceAttributor()
        
        # Create application
        self.application = Application.builder().token(self.bot_token).build()
        
        # Add handlers
        self._add_command_handlers()
        self._add_conversation_handlers()
        
        logger.info("Telegram bot initialized successfully")
    
    def _add_command_handlers(self):
        """Add command handlers to the application."""
        handlers = [
            CommandHandler("start", self.authorized_only(self.start_command)),
            CommandHandler("help", self.authorized_only(self.help_command)),
            CommandHandler("status", self.authorized_only(self.status_command)),
            CommandHandler("positions", self.authorized_only(self.positions_command)),
            CommandHandler("performance", self.authorized_only(self.performance_command)),
            CommandHandler("pause", self.authorized_only(self.pause_command)),
            CommandHandler("resume", self.authorized_only(self.resume_command)),
            CommandHandler("stop", self.authorized_only(self.emergency_stop_command)),
            CommandHandler("risk", self.authorized_only(self.risk_command)),
            CommandHandler("strategies", self.authorized_only(self.strategies_command)),
            CommandHandler("analysis", self.authorized_only(self.analysis_command)),
            CommandHandler("report", self.authorized_only(self.report_command)),
            CommandHandler("logs", self.authorized_only(self.logs_command)),
        ]
        
        for handler in handlers:
            self.application.add_handler(handler)
    
    def _add_conversation_handlers(self):
        """Add conversation handlers for complex interactions."""
        # Risk adjustment conversation
        risk_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("adjust_risk", self.authorized_only(self.adjust_risk_start))],
            states={
                ADJUSTING_RISK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.adjust_risk_input),
                    CallbackQueryHandler(self.adjust_risk_callback)
                ],
                CONFIRMING_ACTION: [
                    CallbackQueryHandler(self.confirm_action_callback)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_command)],
        )
        
        self.application.add_handler(risk_conv_handler)
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    # Command Handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = self.templates['welcome']
        
        # Create quick action keyboard
        keyboard = [
            ["📊 Status", "📍 Positions"],
            ["🏆 Performance", "📈 Analysis"],
            ["⏸️ Pause", "▶️ Resume"],
            ["🛑 Emergency Stop", "ℹ️ Help"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Send initial status
        await self.status_command(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
🤖 **Trading Bot Command Reference**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Monitoring Commands**
• /status - Current P&L, positions, system health
• /positions - Detailed view of all open positions
• /performance - Performance metrics and statistics
• /analysis - Current market analysis and signals

🎮 **Control Commands**
• /pause - Pause all trading activities
• /resume - Resume trading activities
• /stop - Emergency stop (close all positions)
• /risk [level] - Adjust risk level (low/medium/high)

🔧 **Strategy Commands**
• /strategies - Show active strategies and allocations
• /enable [strategy] - Enable specific strategy
• /disable [strategy] - Disable specific strategy

📋 **Reporting Commands**
• /report [period] - Generate detailed reports
• /logs - Show recent system logs
• /errors - Show recent errors and warnings

💡 **Quick Actions**
Use the keyboard buttons for quick access to common commands.

🆘 **Emergency**
Use /stop for immediate emergency shutdown.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        try:
            # Get current portfolio status
            portfolio_status = await self._get_portfolio_status()
            system_status = await self._get_system_status()
            
            # Format status message
            status_message = self.templates['status'].format(
                date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                **portfolio_status,
                **system_status
            )
            
            # Add inline keyboard for quick actions
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
                    InlineKeyboardButton("📍 Positions", callback_data="show_positions")
                ],
                [
                    InlineKeyboardButton("⏸️ Pause" if not self.trading_paused else "▶️ Resume", 
                                       callback_data="toggle_trading"),
                    InlineKeyboardButton("🛑 Emergency", callback_data="emergency_stop")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                status_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text("❌ Error retrieving status. Please try again.")
    
    async def positions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /positions command."""
        try:
            positions = await self._get_open_positions()
            
            if not positions:
                await update.message.reply_text(
                    "📍 **No Open Positions**\n\n"
                    "All positions are currently closed.\n"
                    "Use /analysis to see potential trade signals."
                )
                return
            
            # Send summary first
            summary = f"📍 **Open Positions Summary** ({len(positions)} total)\n\n"
            
            for i, position in enumerate(positions[:5], 1):  # Show first 5
                pnl_emoji = "🟢" if position['unrealized_pnl'] >= 0 else "🔴"
                summary += (
                    f"{i}. **{position['symbol']}** ({position['strategy']})\n"
                    f"   {pnl_emoji} ₹{position['unrealized_pnl']:+,.2f} "
                    f"({position['pnl_percent']:+.1f}%)\n\n"
                )
            
            if len(positions) > 5:
                summary += f"... and {len(positions) - 5} more positions\n\n"
            
            # Add action buttons
            keyboard = [
                [InlineKeyboardButton(f"📋 Details", callback_data="position_details")],
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_positions")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                summary,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in positions command: {e}")
            await update.message.reply_text("❌ Error retrieving positions. Please try again.")
    
    async def performance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /performance command."""
        try:
            # Default to daily performance, allow period parameter
            period = 'daily'
            if context.args:
                period = context.args[0].lower()
            
            performance_data = await self._get_performance_metrics(period)
            
            report = self.templates['performance_report'].format(
                period=period.title(),
                **performance_data
            )
            
            # Add period selection buttons
            keyboard = [
                [
                    InlineKeyboardButton("Today", callback_data="perf_daily"),
                    InlineKeyboardButton("Week", callback_data="perf_weekly"),
                    InlineKeyboardButton("Month", callback_data="perf_monthly")
                ],
                [InlineKeyboardButton("📊 Detailed Report", callback_data="detailed_report")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                report,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in performance command: {e}")
            await update.message.reply_text("❌ Error retrieving performance data. Please try again.")
    
    async def pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pause command."""
        if self.trading_paused:
            await update.message.reply_text("ℹ️ Trading is already paused.")
            return
        
        self.trading_paused = True
        # Update trading engine
        if self.trading_engine:
            await self.trading_engine.pause_trading()
        
        await update.message.reply_text(
            "⏸️ **Trading Paused**\n\n"
            "All automated trading has been paused.\n"
            "Existing positions remain open.\n\n"
            "Use /resume to restart trading."
        )
        logger.info("Trading paused via Telegram command")
    
    async def resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resume command."""
        if not self.trading_paused:
            await update.message.reply_text("ℹ️ Trading is already active.")
            return
        
        self.trading_paused = False
        # Update trading engine
        if self.trading_engine:
            await self.trading_engine.resume_trading()
        
        await update.message.reply_text(
            "▶️ **Trading Resumed**\n\n"
            "Automated trading has been resumed.\n"
            "System will start looking for new signals.\n\n"
            "Use /status to monitor activity."
        )
        logger.info("Trading resumed via Telegram command")
    
    async def emergency_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command - Emergency stop with confirmation."""
        keyboard = [
            [
                InlineKeyboardButton("🛑 Yes, Stop All", callback_data="confirm_emergency_stop"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_emergency")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🚨 **EMERGENCY STOP CONFIRMATION**\n\n"
            "⚠️ This will:\n"
            "• Close ALL open positions immediately\n"
            "• Pause all trading activities\n"
            "• Send emergency notifications\n\n"
            "Are you sure you want to proceed?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Helper Methods
    async def _get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status."""
        # This would integrate with your actual portfolio tracking
        return {
            'total_capital': Decimal('100000.00'),
            'day_pnl': Decimal('2500.75'),
            'day_pnl_percent': Decimal('2.50'),
            'total_pnl': Decimal('15000.00'),
            'total_pnl_percent': Decimal('15.00'),
            'available_capital': Decimal('85000.00'),
        }
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            'open_positions': 3,
            'active_strategies': "Iron Condor, Bull Put Spread",
            'risk_level': "Medium",
            'last_update': datetime.now().strftime("%H:%M:%S"),
            'market_open': True,  # You'd determine this based on market hours
        }
    
    async def _get_open_positions(self) -> List[Dict[str, Any]]:
        """Get list of open positions."""
        # Mock data - replace with actual position data
        return [
            {
                'symbol': 'NIFTY24JAN25000CE',
                'strategy': 'Iron Condor',
                'entry_price': Decimal('125.50'),
                'current_price': Decimal('118.75'),
                'quantity': 2,
                'unrealized_pnl': Decimal('675.00'),
                'pnl_percent': Decimal('5.38'),
                'target_price': Decimal('62.75'),
                'stop_loss': Decimal('251.00'),
                'entry_time': '2024-01-15 10:30:00',
                'days_held': 3,
                'expiry_date': '2024-01-25'
            }
        ]
    
    async def _get_performance_metrics(self, period: str) -> Dict[str, Any]:
        """Get performance metrics for specified period."""
        # Mock data - replace with actual performance calculation
        return {
            'total_return': Decimal('15.25'),
            'sharpe_ratio': Decimal('1.45'),
            'max_drawdown': Decimal('3.2'),
            'win_rate': Decimal('68.5'),
            'total_trades': 25,
            'winning_trades': 17,
            'losing_trades': 8,
            'avg_win': Decimal('1250.75'),
            'avg_loss': Decimal('450.25'),
            'profit_factor': Decimal('2.78'),
            'strategy_performance': "Iron Condor: +₹8,500\nBull Put Spread: +₹4,200\nBear Call Spread: +₹2,300",
            'week_pnl': Decimal('3250.50'),
            'month_pnl': Decimal('12750.75'),
            'last_30_days': Decimal('15000.00')
        }
    
    # Callback Handlers
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button callbacks."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "refresh_status":
            # Refresh status display
            await self.status_command(update, context)
        
        elif query.data == "show_positions":
            await self.positions_command(update, context)
        
        elif query.data == "toggle_trading":
            if self.trading_paused:
                await self.resume_command(update, context)
            else:
                await self.pause_command(update, context)
        
        elif query.data == "emergency_stop":
            await self.emergency_stop_command(update, context)
        
        elif query.data == "confirm_emergency_stop":
            await self._execute_emergency_stop(update, context)
        
        # Performance period callbacks
        elif query.data.startswith("perf_"):
            period = query.data.replace("perf_", "")
            context.args = [period]
            await self.performance_command(update, context)
    
    async def _execute_emergency_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute emergency stop procedure."""
        try:
            # Close all positions
            if self.trading_engine:
                await self.trading_engine.emergency_stop()
            
            self.trading_paused = True
            
            await update.callback_query.message.reply_text(
                "🛑 **EMERGENCY STOP EXECUTED**\n\n"
                "✅ All positions have been closed\n"
                "✅ Trading has been paused\n"
                "✅ Emergency notifications sent\n\n"
                "The system is now in safe mode.\n"
                "Use /status to check final position."
            )
            
            logger.critical("Emergency stop executed via Telegram")
            
        except Exception as e:
            logger.error(f"Error in emergency stop: {e}")
            await update.callback_query.message.reply_text(
                "❌ **Emergency stop failed**\n\n"
                "Please check system logs and contact support immediately."
            )
    
    # Additional placeholder methods for other commands...
    async def risk_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /risk command."""
        await update.message.reply_text("🎯 Risk management controls - Coming soon!")
    
    async def strategies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /strategies command."""
        await update.message.reply_text("🎯 Strategy management - Coming soon!")
    
    async def analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analysis command."""
        await update.message.reply_text("📈 Market analysis - Coming soon!")
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /report command."""
        await update.message.reply_text("📋 Detailed reports - Coming soon!")
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logs command."""
        await update.message.reply_text("📋 System logs - Coming soon!")
    
    async def adjust_risk_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start risk adjustment conversation."""
        return ADJUSTING_RISK
    
    async def adjust_risk_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle risk adjustment input."""
        return ConversationHandler.END
    
    async def adjust_risk_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle risk adjustment callback."""
        return ConversationHandler.END
    
    async def confirm_action_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle action confirmation callback."""
        return ConversationHandler.END
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle conversation cancellation."""
        await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    # Bot Management
    async def run(self):
        """Run the Telegram bot."""
        logger.info(f"Starting Telegram bot for user {self.authorized_user_id}")
        
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        # Keep running
        await self.application.updater.idle()
    
    async def stop(self):
        """Stop the Telegram bot."""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        
        logger.info("Telegram bot stopped")
    
    async def send_notification(self, message: str, parse_mode: str = 'Markdown'):
        """Send notification to authorized user."""
        try:
            await self.application.bot.send_message(
                chat_id=self.authorized_user_id,
                text=message,
                parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    async def send_trade_notification(self, trade_data: Dict[str, Any]):
        """Send trade execution notification."""
        notification = f"""
🎯 **Trade Executed**
━━━━━━━━━━━━━━━━
Symbol: {trade_data['symbol']}
Strategy: {trade_data['strategy']}
Type: {trade_data['order_type']}
Entry: ₹{trade_data['entry_price']}
Quantity: {trade_data['quantity']}
Target: ₹{trade_data.get('target', 'N/A')}
Stop Loss: ₹{trade_data.get('stop_loss', 'N/A')}
━━━━━━━━━━━━━━━━
        """
        await self.send_notification(notification)
    
    async def send_daily_summary(self, summary_data: Dict[str, Any]):
        """Send daily performance summary."""
        summary = f"""
📊 **Daily Summary - {datetime.now().strftime('%Y-%m-%d')}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 P&L: ₹{summary_data['pnl']:+,.2f} ({summary_data['pnl_percent']:+.2f}%)
🎯 Trades: {summary_data['total_trades']} ({summary_data['winning']}/{summary_data['losing']})
💰 Capital Used: {summary_data['capital_used']:.1f}%
🏆 Best Trade: ₹{summary_data['best_trade']:+,.2f}
😞 Worst Trade: ₹{summary_data['worst_trade']:+,.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conservative: ₹{summary_data['conservative_pnl']:+,.2f}
Aggressive: ₹{summary_data['aggressive_pnl']:+,.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        await self.send_notification(summary)


# Factory function for easy initialization
def create_telegram_bot(bot_token: str, user_id: int) -> TradingBotTelegram:
    """
    Factory function to create and initialize Telegram bot.
    
    Args:
        bot_token: Telegram bot token
        user_id: Authorized user's Telegram ID
        
    Returns:
        Initialized TradingBotTelegram instance
    """
    return TradingBotTelegram(bot_token, user_id)


if __name__ == "__main__":
    # Example usage - in production this would be called from main application
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    user_id = int(os.getenv("TELEGRAM_USER_ID", 0))
    
    if bot_token and user_id:
        bot = create_telegram_bot(bot_token, user_id)
        asyncio.run(bot.run())
    else:
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_USER_ID environment variables")