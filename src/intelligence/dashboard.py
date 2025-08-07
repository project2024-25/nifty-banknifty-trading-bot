from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path

from .market_regime import MarketRegimeDetector, MarketConditions
from .strategy_selector import AdaptiveStrategySelector, StrategyAllocation
from .dynamic_allocator import DynamicAllocationManager, PortfolioAllocation
from ..strategies.base_strategy import MarketData
from ..utils.logger import get_logger


@dataclass
class DashboardMetrics:
    """Dashboard metrics snapshot"""
    timestamp: datetime
    market_conditions: MarketConditions
    strategy_allocations: List[StrategyAllocation]
    portfolio_summary: Dict
    active_signals_count: int
    total_capital_deployed: float
    risk_utilization: float
    expected_portfolio_return: float
    confidence_score: float


class MarketConditionsDashboard:
    """Real-time market conditions and strategy dashboard"""
    
    def __init__(self, capital: float = 1000000):
        self.logger = get_logger("dashboard")
        
        # Initialize components
        self.regime_detector = MarketRegimeDetector()
        self.strategy_selector = AdaptiveStrategySelector()
        self.allocation_manager = DynamicAllocationManager(total_capital=capital)
        
        # Dashboard state
        self.current_metrics: Optional[DashboardMetrics] = None
        self.metrics_history: List[DashboardMetrics] = []
        self.max_history_size = 100
        
        # Dashboard configuration
        self.dashboard_config = {
            'refresh_interval_seconds': 60,
            'save_metrics_history': True,
            'metrics_file': 'market_dashboard_history.json'
        }
    
    async def update_dashboard(self, market_data: MarketData) -> DashboardMetrics:
        """Update dashboard with latest market data"""
        
        try:
            # Step 1: Detect market regime and conditions
            market_conditions = self.regime_detector.detect_regime(market_data)
            
            # Step 2: Get optimal strategy allocations
            strategy_allocations = await self.strategy_selector.select_strategies(market_data)
            
            # Step 3: Generate adaptive signals
            signals = await self.strategy_selector.generate_adaptive_signals(market_data)
            
            # Step 4: Create portfolio allocation if signals exist
            portfolio_allocation = None
            if signals:
                portfolio_allocation = self.allocation_manager.allocate_portfolio(
                    signals, market_conditions
                )
                self.allocation_manager.update_positions(portfolio_allocation)
            
            # Step 5: Get portfolio summary
            portfolio_summary = self.allocation_manager.get_portfolio_summary()
            
            # Step 6: Create dashboard metrics
            metrics = DashboardMetrics(
                timestamp=datetime.now(),
                market_conditions=market_conditions,
                strategy_allocations=strategy_allocations,
                portfolio_summary=portfolio_summary,
                active_signals_count=len(signals) if signals else 0,
                total_capital_deployed=portfolio_allocation.total_capital_used if portfolio_allocation else 0,
                risk_utilization=portfolio_allocation.total_risk_allocated if portfolio_allocation else 0,
                expected_portfolio_return=portfolio_allocation.expected_return if portfolio_allocation else 0,
                confidence_score=market_conditions.confidence_score
            )
            
            # Update dashboard state
            self.current_metrics = metrics
            self._add_to_history(metrics)
            
            # Save metrics if configured
            if self.dashboard_config['save_metrics_history']:
                self._save_metrics_history()
            
            self.logger.info(
                "Dashboard updated successfully",
                regime=market_conditions.regime.value,
                strategies_selected=len(strategy_allocations),
                signals_generated=len(signals) if signals else 0,
                capital_deployed=metrics.total_capital_deployed
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Dashboard update failed: {e}")
            raise
    
    def display_dashboard(self, metrics: Optional[DashboardMetrics] = None) -> str:
        """Generate formatted dashboard display"""
        
        if metrics is None:
            metrics = self.current_metrics
        
        if metrics is None:
            return "Dashboard not initialized. Update with market data first."
        
        # Build dashboard display
        dashboard_lines = []
        
        # Header
        dashboard_lines.extend([
            "=" * 80,
            "ALGO TRADING BOT - MARKET CONDITIONS DASHBOARD",
            "=" * 80,
            f"Last Updated: {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ])
        
        # Market Conditions Section
        mc = metrics.market_conditions
        dashboard_lines.extend([
            "📊 MARKET CONDITIONS",
            "-" * 40,
            f"Market Regime:        {mc.regime.value.replace('_', ' ').title()}",
            f"Volatility Regime:    {mc.volatility_regime.value.title()} ({mc.iv_percentile:.0f}th percentile)",
            f"Trend Direction:      {mc.trend_direction.title()} ({mc.trend_strength.value})",
            f"Current IV:           {mc.current_iv:.1f}% (Avg: {mc.historical_iv_avg:.1f}%)",
            f"Momentum Score:       {mc.momentum_score:+.2f}",
            f"Mean Reversion:       {mc.mean_reversion_likelihood:.1%}",
            f"Breakout Probability: {mc.breakout_probability:.1%}",
            f"Detection Confidence: {mc.confidence_score:.1%}",
            ""
        ])
        
        # Strategy Selection Section
        dashboard_lines.extend([
            "🎯 STRATEGY SELECTION",
            "-" * 40
        ])
        
        if metrics.strategy_allocations:
            dashboard_lines.append(f"Selected Strategies: {len(metrics.strategy_allocations)}")
            dashboard_lines.append("")
            dashboard_lines.append("Strategy             Weight    Max Pos  Priority")
            dashboard_lines.append("-" * 48)
            
            for allocation in metrics.strategy_allocations:
                name = allocation.strategy_name.replace('_', ' ').title()
                dashboard_lines.append(
                    f"{name:<20} {allocation.allocation_weight:>6.1%}    "
                    f"{allocation.max_positions:>3}      {allocation.priority:>3}"
                )
        else:
            dashboard_lines.append("No strategies selected for current market conditions")
        
        dashboard_lines.append("")
        
        # Portfolio Status Section
        ps = metrics.portfolio_summary
        dashboard_lines.extend([
            "💼 PORTFOLIO STATUS",
            "-" * 40,
            f"Total Capital:        Rs.{ps['total_capital']:>12,.0f}",
            f"Deployed Capital:     Rs.{metrics.total_capital_deployed:>12,.0f} ({metrics.total_capital_deployed/ps['total_capital']:.1%})",
            f"Available Capital:    Rs.{ps['available_capital']:>12,.0f}",
            f"Active Positions:     {ps['total_positions']:>12}",
            f"Risk Utilization:     {metrics.risk_utilization:>12.1%}",
            f"Expected Return:      Rs.{metrics.expected_portfolio_return:>12,.0f}",
            ""
        ])
        
        # Signals Section
        dashboard_lines.extend([
            "📈 TRADING SIGNALS",
            "-" * 40,
            f"Active Signals:       {metrics.active_signals_count}",
            f"Overall Confidence:   {metrics.confidence_score:.1%}",
            ""
        ])
        
        # Performance Indicators
        dashboard_lines.extend([
            "⚡ KEY INDICATORS",
            "-" * 40,
            self._get_regime_status_indicator(mc.regime.value),
            self._get_volatility_status_indicator(mc.volatility_regime.value, mc.iv_percentile),
            self._get_trend_status_indicator(mc.trend_direction, mc.trend_strength.value),
            self._get_risk_status_indicator(metrics.risk_utilization),
            ""
        ])
        
        # Footer
        dashboard_lines.extend([
            "=" * 80,
            f"Dashboard powered by Adaptive Strategy Selection Engine v1.0",
            "=" * 80
        ])
        
        return "\n".join(dashboard_lines)
    
    def get_regime_summary(self) -> Dict:
        """Get current market regime summary"""
        if not self.current_metrics:
            return {}
        
        mc = self.current_metrics.market_conditions
        return {
            'regime': mc.regime.value,
            'volatility_regime': mc.volatility_regime.value,
            'trend_direction': mc.trend_direction,
            'trend_strength': mc.trend_strength.value,
            'confidence': mc.confidence_score,
            'iv_percentile': mc.iv_percentile,
            'momentum_score': mc.momentum_score,
            'breakout_probability': mc.breakout_probability
        }
    
    def get_strategy_performance_summary(self) -> Dict:
        """Get strategy selection performance summary"""
        if not self.current_metrics:
            return {}
        
        return {
            'strategies_selected': len(self.current_metrics.strategy_allocations),
            'signals_generated': self.current_metrics.active_signals_count,
            'capital_deployment_rate': (
                self.current_metrics.total_capital_deployed / 
                self.current_metrics.portfolio_summary['total_capital']
            ),
            'risk_utilization': self.current_metrics.risk_utilization,
            'expected_return': self.current_metrics.expected_portfolio_return
        }
    
    def get_historical_trends(self, lookback_periods: int = 10) -> Dict:
        """Get historical trend analysis"""
        if len(self.metrics_history) < 2:
            return {'error': 'Insufficient historical data'}
        
        recent_metrics = self.metrics_history[-lookback_periods:]
        
        # Calculate trends
        regime_changes = len(set(m.market_conditions.regime for m in recent_metrics))
        avg_confidence = sum(m.confidence_score for m in recent_metrics) / len(recent_metrics)
        avg_signals = sum(m.active_signals_count for m in recent_metrics) / len(recent_metrics)
        
        return {
            'periods_analyzed': len(recent_metrics),
            'regime_stability': regime_changes / len(recent_metrics),
            'avg_detection_confidence': avg_confidence,
            'avg_signals_per_period': avg_signals,
            'most_common_regime': max(
                set(m.market_conditions.regime.value for m in recent_metrics),
                key=lambda x: sum(1 for m in recent_metrics if m.market_conditions.regime.value == x)
            )
        }
    
    def _add_to_history(self, metrics: DashboardMetrics):
        """Add metrics to history with size management"""
        self.metrics_history.append(metrics)
        
        # Maintain max history size
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def _save_metrics_history(self):
        """Save metrics history to file"""
        try:
            # Convert to serializable format
            history_data = []
            for metrics in self.metrics_history[-20:]:  # Save last 20 entries
                data = {
                    'timestamp': metrics.timestamp.isoformat(),
                    'regime': metrics.market_conditions.regime.value,
                    'volatility_regime': metrics.market_conditions.volatility_regime.value,
                    'confidence': metrics.confidence_score,
                    'strategies_count': len(metrics.strategy_allocations),
                    'signals_count': metrics.active_signals_count,
                    'capital_deployed': metrics.total_capital_deployed,
                    'risk_utilization': metrics.risk_utilization
                }
                history_data.append(data)
            
            # Save to file
            with open(self.dashboard_config['metrics_file'], 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to save metrics history: {e}")
    
    def _get_regime_status_indicator(self, regime: str) -> str:
        """Get regime status indicator"""
        regime_indicators = {
            'bull_trending': '🟢 BULL TRENDING - Directional strategies favored',
            'bear_trending': '🔴 BEAR TRENDING - Put strategies recommended',
            'bull_volatile': '🟡 BULL VOLATILE - Long volatility strategies',
            'bear_volatile': '🟡 BEAR VOLATILE - Protective strategies active',
            'sideways_low_vol': '🔵 SIDEWAYS LOW VOL - Premium selling optimal',
            'sideways_high_vol': '🟠 SIDEWAYS HIGH VOL - Range trading active',
            'breakout_pending': '⚪ BREAKOUT PENDING - Volatility plays ready',
            'high_uncertainty': '⚫ HIGH UNCERTAINTY - Conservative approach'
        }
        return regime_indicators.get(regime, f'Regime: {regime}')
    
    def _get_volatility_status_indicator(self, vol_regime: str, percentile: float) -> str:
        """Get volatility status indicator"""
        if vol_regime == 'extreme':
            return f'⚠️  EXTREME VOLATILITY - {percentile:.0f}th percentile - High premium collection opportunity'
        elif vol_regime == 'high':
            return f'🔥 HIGH VOLATILITY - {percentile:.0f}th percentile - Premium selling favored'
        elif vol_regime == 'low':
            return f'❄️  LOW VOLATILITY - {percentile:.0f}th percentile - Premium buying opportunity'
        else:
            return f'📊 NORMAL VOLATILITY - {percentile:.0f}th percentile - Balanced strategies'
    
    def _get_trend_status_indicator(self, direction: str, strength: str) -> str:
        """Get trend status indicator"""
        if strength == 'strong':
            if direction == 'bullish':
                return '📈 STRONG BULL TREND - Calls and bull spreads optimal'
            elif direction == 'bearish':
                return '📉 STRONG BEAR TREND - Puts and bear spreads optimal'
        elif strength == 'moderate':
            return f'➡️  MODERATE {direction.upper()} TREND - Directional bias present'
        elif strength == 'weak':
            return '〰️  WEAK TREND - Mixed signals, range strategies considered'
        else:
            return '🔄 NO CLEAR TREND - Neutral strategies recommended'
    
    def _get_risk_status_indicator(self, risk_utilization: float) -> str:
        """Get risk status indicator"""
        if risk_utilization > 0.08:  # > 8%
            return '🔴 HIGH RISK UTILIZATION - Monitor positions closely'
        elif risk_utilization > 0.05:  # > 5%
            return '🟡 MODERATE RISK UTILIZATION - Good deployment level'
        elif risk_utilization > 0.02:  # > 2%
            return '🟢 CONSERVATIVE RISK UTILIZATION - Safe deployment'
        else:
            return '⚪ LOW RISK UTILIZATION - Opportunity for more deployment'