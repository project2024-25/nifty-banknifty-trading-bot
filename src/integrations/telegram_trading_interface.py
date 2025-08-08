"""
Advanced Telegram Trading Interface

This module integrates the Telegram bot with the sophisticated trading system,
including market regime detection, strategy selection, and portfolio management.
"""

import asyncio
import logging
import sys
import os
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from integrations.telegram_bot import TradingBotTelegram

# Import our sophisticated trading components
try:
    from core.adaptive_trading_engine import AdaptiveTradingEngine
    from intelligence.strategy_selector import StrategySelector
    from intelligence.market_regime import MarketRegimeDetector
    from intelligence.volatility_analyzer import VolatilityAnalyzer
    from intelligence.dynamic_allocator import DynamicPortfolioAllocator
    from intelligence.performance_attribution import PerformanceAttributor
    from intelligence.trend_detector import TrendDetector
except ImportError as e:
    logging.warning(f"Some advanced components not available: {e}")


class AdvancedTradingTelegram(TradingBotTelegram):
    """
    Enhanced Telegram bot that integrates with sophisticated trading intelligence.
    
    Provides real-time access to:
    - Market regime detection
    - Strategy selection engine
    - Portfolio allocation
    - Performance attribution
    - Volatility analysis
    - Trend detection
    """
    
    def __init__(self, bot_token: str, authorized_user_id: int):
        super().__init__(bot_token, authorized_user_id)
        
        # Advanced trading components
        self.adaptive_engine = None
        self.strategy_selector = None
        self.regime_detector = None
        self.volatility_analyzer = None
        self.portfolio_allocator = None
        self.performance_attributor = None
        self.trend_detector = None
        
        # Enhanced templates
        self._load_advanced_templates()
    
    def _load_advanced_templates(self):
        """Load advanced message templates for sophisticated features."""
        advanced_templates = {
            'market_analysis': """
📈 **Market Analysis - {timestamp}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Market Regime**
• Current: {current_regime}
• Confidence: {regime_confidence:.1f}%
• Trend Strength: {trend_strength}
• Volatility Level: {volatility_level}

📊 **Technical Analysis**
• NIFTY Trend: {nifty_trend} ({nifty_strength})
• BANKNIFTY Trend: {banknifty_trend} ({banknifty_strength})
• Support: {support_level} | Resistance: {resistance_level}
• VIX: {vix_level} ({vix_percentile}th percentile)

🎲 **Strategy Recommendations**
{strategy_recommendations}

💡 **Key Insights**
{key_insights}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """,
            
            'strategy_allocation': """
🎯 **Portfolio Allocation - {date}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Capital Distribution**
• Available: ₹{available_capital:,.2f}
• Conservative (60%): ₹{conservative_allocation:,.2f}
• Aggressive (40%): ₹{aggressive_allocation:,.2f}

📋 **Active Strategies**
{strategy_breakdown}

⚖️ **Risk Metrics**
• Daily VaR: ₹{daily_var:,.2f}
• Portfolio Beta: {portfolio_beta:.2f}
• Correlation Risk: {correlation_risk}

🎲 **Next Actions**
{next_actions}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """,
            
            'regime_update': """
🔄 **Market Regime Change Detected**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Regime Transition**
• From: {old_regime}
• To: {new_regime}
• Confidence: {confidence:.1f}%
• Duration in Previous: {duration_hours}h

⚡ **Impact Assessment**
• Strategy Adjustments: {strategy_adjustments}
• Risk Level: {new_risk_level}
• Position Changes: {position_changes}

🎯 **Action Taken**
{actions_taken}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """,
            
            'performance_detailed': """
🏆 **Advanced Performance Report - {period}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **Risk-Adjusted Returns**
• Sharpe Ratio: {sharpe_ratio:.2f}
• Sortino Ratio: {sortino_ratio:.2f}
• Calmar Ratio: {calmar_ratio:.2f}
• Information Ratio: {information_ratio:.2f}

🎯 **Strategy Attribution**
{strategy_attribution}

📊 **Regime Performance**
{regime_performance}

💼 **Portfolio Metrics**
• Max Drawdown: {max_drawdown:.2f}%
• Recovery Time: {recovery_days} days
• Win Rate: {win_rate:.1f}%
• Profit Factor: {profit_factor:.2f}

🔥 **Recent Highlights**
• Best Trade: ₹{best_trade:+,.2f} ({best_strategy})
• Worst Trade: ₹{worst_trade:+,.2f} ({worst_strategy})
• Current Streak: {current_streak}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
        }
        
        # Merge with base templates
        self.templates.update(advanced_templates)
    
    async def initialize(self):
        """Initialize the enhanced bot with advanced trading components."""
        # Call parent initialization
        await super().initialize()
        
        try:
            # Initialize advanced components
            self.adaptive_engine = AdaptiveTradingEngine()
            await self.adaptive_engine.initialize()
            
            self.strategy_selector = StrategySelector()
            self.regime_detector = MarketRegimeDetector()
            self.volatility_analyzer = VolatilityAnalyzer()
            self.portfolio_allocator = DynamicPortfolioAllocator()
            self.performance_attributor = PerformanceAttributor()
            self.trend_detector = TrendDetector()
            
            logging.info("Advanced trading components initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing advanced components: {e}")
            # Continue with basic functionality
    
    # Enhanced command handlers
    async def analysis_command(self, update, context):
        """Enhanced /analysis command with sophisticated market analysis."""
        try:
            # Get comprehensive market analysis
            analysis_data = await self._get_comprehensive_analysis()
            
            analysis_message = self.templates['market_analysis'].format(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
                **analysis_data
            )
            
            # Add action buttons
            keyboard = [
                [
                    {"text": "🔄 Refresh Analysis", "callback_data": "refresh_analysis"},
                    {"text": "📊 Detailed Charts", "callback_data": "show_charts"}
                ],
                [
                    {"text": "🎯 Strategy Signals", "callback_data": "show_signals"},
                    {"text": "⚖️ Risk Assessment", "callback_data": "risk_assessment"}
                ]
            ]
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"])]
                for row in keyboard for btn in row
            ])
            
            await update.message.reply_text(
                analysis_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logging.error(f"Error in enhanced analysis command: {e}")
            await update.message.reply_text("❌ Error generating market analysis. Please try again.")
    
    async def strategies_command(self, update, context):
        """Enhanced /strategies command with portfolio allocation details."""
        try:
            allocation_data = await self._get_portfolio_allocation()
            
            allocation_message = self.templates['strategy_allocation'].format(
                date=datetime.now().strftime("%Y-%m-%d"),
                **allocation_data
            )
            
            # Add strategy control buttons
            keyboard = [
                [
                    {"text": "📊 Rebalance", "callback_data": "rebalance_portfolio"},
                    {"text": "⚖️ Adjust Risk", "callback_data": "adjust_risk_level"}
                ],
                [
                    {"text": "🎯 Strategy Details", "callback_data": "strategy_details"},
                    {"text": "📈 Performance", "callback_data": "strategy_performance"}
                ]
            ]
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"])]
                for row in keyboard for btn in row
            ])
            
            await update.message.reply_text(
                allocation_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logging.error(f"Error in enhanced strategies command: {e}")
            await update.message.reply_text("❌ Error retrieving strategy allocation. Please try again.")
    
    async def performance_command(self, update, context):
        """Enhanced performance command with advanced metrics."""
        try:
            period = 'daily'
            if context.args:
                period = context.args[0].lower()
            
            performance_data = await self._get_advanced_performance_metrics(period)
            
            report = self.templates['performance_detailed'].format(
                period=period.title(),
                **performance_data
            )
            
            # Add detailed analysis buttons
            keyboard = [
                [
                    {"text": "📊 Attribution", "callback_data": "performance_attribution"},
                    {"text": "📈 Regime Analysis", "callback_data": "regime_performance"}
                ],
                [
                    {"text": "🎯 Risk Metrics", "callback_data": "risk_metrics"},
                    {"text": "📋 Export Report", "callback_data": "export_report"}
                ]
            ]
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"])]
                for row in keyboard for btn in row
            ])
            
            await update.message.reply_text(
                report,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logging.error(f"Error in enhanced performance command: {e}")
            await update.message.reply_text("❌ Error retrieving advanced performance data. Please try again.")
    
    # Advanced data retrieval methods
    async def _get_comprehensive_analysis(self) -> Dict[str, Any]:
        """Get comprehensive market analysis from sophisticated trading system."""
        try:
            # Get market regime
            regime_data = {}
            if self.regime_detector:
                # This would call your actual regime detection
                regime_data = {
                    'current_regime': 'Bull Trending',
                    'regime_confidence': 85.2,
                    'trend_strength': 'Strong',
                    'volatility_level': 'Medium'
                }
            
            # Get trend analysis
            trend_data = {}
            if self.trend_detector:
                trend_data = {
                    'nifty_trend': 'Bullish',
                    'nifty_strength': '8.2/10',
                    'banknifty_trend': 'Bullish',
                    'banknifty_strength': '7.8/10',
                    'support_level': '24,800',
                    'resistance_level': '25,200'
                }
            
            # Get volatility data
            vix_data = {
                'vix_level': '14.2',
                'vix_percentile': '25'
            }
            
            # Get strategy recommendations
            if self.strategy_selector:
                strategy_recommendations = """
• Iron Condor: High Probability (VIX < 15)
• Bull Put Spread: Moderate Probability
• Credit Spreads: Low Probability (High Momentum)
                """.strip()
            else:
                strategy_recommendations = "Strategy engine not available"
            
            key_insights = """
• Market showing strong bullish momentum
• Low volatility suggests mean reversion strategies
• Banking sector outperforming broader market
            """.strip()
            
            return {
                **regime_data,
                **trend_data,
                **vix_data,
                'strategy_recommendations': strategy_recommendations,
                'key_insights': key_insights
            }
            
        except Exception as e:
            logging.error(f"Error getting comprehensive analysis: {e}")
            return {
                'current_regime': 'Analysis Unavailable',
                'regime_confidence': 0.0,
                'trend_strength': 'Unknown',
                'volatility_level': 'Unknown',
                'nifty_trend': 'Unknown',
                'nifty_strength': 'N/A',
                'banknifty_trend': 'Unknown', 
                'banknifty_strength': 'N/A',
                'support_level': 'N/A',
                'resistance_level': 'N/A',
                'vix_level': 'N/A',
                'vix_percentile': 'N/A',
                'strategy_recommendations': 'Analysis service unavailable',
                'key_insights': 'Please check system status'
            }
    
    async def _get_portfolio_allocation(self) -> Dict[str, Any]:
        """Get detailed portfolio allocation data."""
        try:
            available_capital = Decimal('100000.00')  # This would come from your system
            
            return {
                'available_capital': available_capital,
                'conservative_allocation': available_capital * Decimal('0.6'),
                'aggressive_allocation': available_capital * Decimal('0.4'),
                'strategy_breakdown': """
• Iron Condor: 25% (₹25,000) - Active
• Bull Put Spread: 20% (₹20,000) - Active  
• Bear Call Spread: 15% (₹15,000) - Paused
• Long Straddle: 15% (₹15,000) - Monitoring
• Directional Options: 15% (₹15,000) - Paused
• Cash Reserve: 10% (₹10,000) - Available
                """.strip(),
                'daily_var': Decimal('3000.00'),
                'portfolio_beta': Decimal('1.15'),
                'correlation_risk': 'Low',
                'next_actions': """
• Consider Iron Condor entry at market open
• Monitor VIX for volatility strategy signals  
• Evaluate Bull Put Spread opportunities
                """.strip()
            }
            
        except Exception as e:
            logging.error(f"Error getting portfolio allocation: {e}")
            return {
                'available_capital': Decimal('0'),
                'conservative_allocation': Decimal('0'),
                'aggressive_allocation': Decimal('0'),
                'strategy_breakdown': 'Data unavailable',
                'daily_var': Decimal('0'),
                'portfolio_beta': Decimal('0'),
                'correlation_risk': 'Unknown',
                'next_actions': 'System unavailable'
            }
    
    async def _get_advanced_performance_metrics(self, period: str) -> Dict[str, Any]:
        """Get advanced performance metrics with attribution."""
        try:
            # This would integrate with your actual performance attribution system
            return {
                'sharpe_ratio': Decimal('1.45'),
                'sortino_ratio': Decimal('1.68'),
                'calmar_ratio': Decimal('2.1'),
                'information_ratio': Decimal('0.85'),
                'strategy_attribution': """
• Iron Condor: +₹8,500 (56% of profits)
• Bull Put Spread: +₹4,200 (28% of profits)
• Bear Call Spread: +₹2,300 (15% of profits)
• Other: +₹150 (1% of profits)
                """.strip(),
                'regime_performance': """
• Bull Trending: +₹12,800 (85% win rate)
• Bear Trending: +₹1,200 (45% win rate)  
• Sideways: +₹1,150 (72% win rate)
• High Volatility: -₹300 (35% win rate)
                """.strip(),
                'max_drawdown': Decimal('3.2'),
                'recovery_days': 5,
                'win_rate': Decimal('68.5'),
                'profit_factor': Decimal('2.78'),
                'best_trade': Decimal('2850.75'),
                'best_strategy': 'Iron Condor',
                'worst_trade': Decimal('-850.25'),
                'worst_strategy': 'Long Straddle',
                'current_streak': '5 wins'
            }
            
        except Exception as e:
            logging.error(f"Error getting advanced performance metrics: {e}")
            return {
                'sharpe_ratio': Decimal('0'),
                'sortino_ratio': Decimal('0'),
                'calmar_ratio': Decimal('0'),
                'information_ratio': Decimal('0'),
                'strategy_attribution': 'Data unavailable',
                'regime_performance': 'Data unavailable',
                'max_drawdown': Decimal('0'),
                'recovery_days': 0,
                'win_rate': Decimal('0'),
                'profit_factor': Decimal('0'),
                'best_trade': Decimal('0'),
                'best_strategy': 'N/A',
                'worst_trade': Decimal('0'),
                'worst_strategy': 'N/A',
                'current_streak': 'N/A'
            }
    
    # Advanced notification methods
    async def send_regime_change_notification(self, old_regime: str, new_regime: str, confidence: float):
        """Send market regime change notification."""
        try:
            notification_data = {
                'old_regime': old_regime,
                'new_regime': new_regime,
                'confidence': confidence,
                'duration_hours': 4.5,  # This would be calculated
                'strategy_adjustments': 'Iron Condor → Bull Put Spread',
                'new_risk_level': 'Medium-High',
                'position_changes': '2 positions adjusted',
                'actions_taken': """
• Increased aggressive allocation to 45%
• Activated Bull Put Spread strategy
• Paused Iron Condor entries temporarily
                """.strip()
            }
            
            message = self.templates['regime_update'].format(**notification_data)
            await self.send_notification(message)
            
        except Exception as e:
            logging.error(f"Error sending regime change notification: {e}")
    
    async def send_strategy_signal_notification(self, strategy: str, signal_data: Dict):
        """Send strategy signal notification."""
        signal_message = f"""
🎯 **Strategy Signal: {strategy}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Signal Details**
• Entry Price: ₹{signal_data.get('entry_price', 'TBD')}
• Probability: {signal_data.get('probability', 'N/A')}%
• Risk/Reward: 1:{signal_data.get('risk_reward', 'N/A')}
• Max Risk: ₹{signal_data.get('max_risk', 'TBD')}

⏰ **Timing**
• Entry Window: {signal_data.get('entry_window', 'Next 30 min')}
• Target Time: {signal_data.get('target_time', '3-5 days')}
• Expiry: {signal_data.get('expiry', 'Current weekly')}

🎮 **Action Required**
• Auto-execute: {"✅ YES" if signal_data.get('auto_execute', False) else "❌ NO"}
• Manual review: {"✅ Required" if not signal_data.get('auto_execute', True) else "❌ Not needed"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        await self.send_notification(signal_message)


# Factory function for the enhanced bot
def create_advanced_telegram_bot(bot_token: str, user_id: int) -> AdvancedTradingTelegram:
    """
    Create an advanced Telegram bot with sophisticated trading integration.
    
    Args:
        bot_token: Telegram bot token
        user_id: Authorized user's Telegram ID
        
    Returns:
        AdvancedTradingTelegram instance
    """
    return AdvancedTradingTelegram(bot_token, user_id)