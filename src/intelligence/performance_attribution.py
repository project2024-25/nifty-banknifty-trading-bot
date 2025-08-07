from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
import json

from .market_regime import MarketRegime, VolatilityRegime, TrendStrength
from ..strategies.base_strategy import StrategySignal
from ..utils.logger import get_logger


class AttributionPeriod(Enum):
    """Performance attribution time periods"""
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PerformanceCategory(Enum):
    """Categories for performance classification"""
    EXCELLENT = "excellent"      # > 90th percentile
    GOOD = "good"               # 70-90th percentile
    AVERAGE = "average"         # 30-70th percentile
    POOR = "poor"               # 10-30th percentile
    VERY_POOR = "very_poor"     # < 10th percentile


@dataclass
class TradePerformance:
    """Individual trade performance metrics"""
    trade_id: str
    strategy_name: str
    symbol: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    
    # Trade details
    position_size: int = 1
    max_profit: float = 0.0
    max_loss: float = 0.0
    actual_pnl: float = 0.0
    
    # Market context
    entry_regime: Optional[MarketRegime] = None
    entry_volatility: Optional[VolatilityRegime] = None
    entry_confidence: float = 0.0
    
    # Performance metrics
    win_rate: float = 0.0
    profit_factor: float = 0.0
    risk_reward_ratio: float = 0.0
    days_held: int = 0
    
    # Attribution factors
    regime_contribution: float = 0.0
    timing_contribution: float = 0.0
    sizing_contribution: float = 0.0
    
    # Status
    is_closed: bool = False
    close_reason: str = ""


@dataclass
class StrategyAttribution:
    """Strategy-level performance attribution"""
    strategy_name: str
    period_start: datetime
    period_end: datetime
    
    # Basic metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    
    # Performance ratios
    win_rate: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    
    # Regime attribution
    regime_performance: Dict[str, float] = field(default_factory=dict)
    volatility_performance: Dict[str, float] = field(default_factory=dict)
    
    # Risk metrics
    var_95: float = 0.0  # Value at Risk 95%
    expected_shortfall: float = 0.0
    
    # Timing analysis
    best_entry_times: List[Tuple[str, float]] = field(default_factory=list)
    worst_entry_times: List[Tuple[str, float]] = field(default_factory=list)
    
    # Attribution breakdown
    alpha_contribution: float = 0.0  # Strategy skill
    beta_contribution: float = 0.0   # Market direction
    regime_contribution: float = 0.0  # Regime selection
    timing_contribution: float = 0.0  # Entry/exit timing


@dataclass
class RegimeAttribution:
    """Regime-level performance attribution"""
    regime: MarketRegime
    period_start: datetime
    period_end: datetime
    
    # Regime occurrence
    total_periods: int = 0
    regime_periods: int = 0
    regime_frequency: float = 0.0
    
    # Performance in this regime
    strategies_used: List[str] = field(default_factory=list)
    total_regime_pnl: float = 0.0
    average_regime_pnl: float = 0.0
    regime_win_rate: float = 0.0
    
    # Best/worst strategies in this regime
    best_strategy: Optional[str] = None
    best_strategy_pnl: float = 0.0
    worst_strategy: Optional[str] = None
    worst_strategy_pnl: float = 0.0
    
    # Regime transition performance
    transition_from_performance: Dict[str, float] = field(default_factory=dict)
    transition_to_performance: Dict[str, float] = field(default_factory=dict)


class PerformanceAttributionEngine:
    """Advanced performance attribution and analysis engine"""
    
    def __init__(self):
        self.logger = get_logger("performance_attribution")
        
        # Performance data storage
        self.trade_history: List[TradePerformance] = []
        self.strategy_attributions: Dict[str, List[StrategyAttribution]] = {}
        self.regime_attributions: Dict[str, List[RegimeAttribution]] = {}
        
        # Benchmarks and baselines
        self.market_benchmark_returns: List[Tuple[datetime, float]] = []
        self.risk_free_rate = 0.07  # 7% annual risk-free rate
        
        # Configuration
        self.attribution_config = {
            'min_trades_for_attribution': 10,
            'lookback_periods': 252,  # 1 year of trading days
            'confidence_intervals': [0.90, 0.95, 0.99],
            'rebalance_frequency': 30,  # days
        }
    
    def add_trade_performance(self, trade_data: Dict[str, Any], 
                            regime_context: Optional[Dict[str, Any]] = None):
        """Add a completed trade for performance attribution"""
        
        try:
            trade = TradePerformance(
                trade_id=trade_data.get('trade_id', ''),
                strategy_name=trade_data.get('strategy_name', ''),
                symbol=trade_data.get('symbol', ''),
                entry_time=trade_data.get('entry_time', datetime.now()),
                exit_time=trade_data.get('exit_time'),
                position_size=trade_data.get('position_size', 1),
                max_profit=trade_data.get('max_profit', 0.0),
                max_loss=trade_data.get('max_loss', 0.0),
                actual_pnl=trade_data.get('actual_pnl', 0.0),
                is_closed=trade_data.get('is_closed', False),
                close_reason=trade_data.get('close_reason', '')
            )
            
            # Add regime context if available
            if regime_context:
                trade.entry_regime = regime_context.get('regime')
                trade.entry_volatility = regime_context.get('volatility_regime')
                trade.entry_confidence = regime_context.get('confidence', 0.0)
            
            # Calculate derived metrics
            if trade.exit_time and trade.entry_time:
                trade.days_held = (trade.exit_time - trade.entry_time).days
            
            if trade.max_loss != 0:
                trade.risk_reward_ratio = abs(trade.max_profit / trade.max_loss)
            
            self.trade_history.append(trade)
            
            self.logger.info(
                "Trade added to performance attribution",
                trade_id=trade.trade_id,
                strategy=trade.strategy_name,
                pnl=trade.actual_pnl,
                regime=trade.entry_regime.value if trade.entry_regime else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add trade performance: {e}")
    
    def calculate_strategy_attribution(self, strategy_name: str, 
                                     period: AttributionPeriod = AttributionPeriod.MONTHLY) -> StrategyAttribution:
        """Calculate detailed performance attribution for a strategy"""
        
        try:
            # Get date range for period
            end_date = datetime.now()
            if period == AttributionPeriod.DAILY:
                start_date = end_date - timedelta(days=1)
            elif period == AttributionPeriod.WEEKLY:
                start_date = end_date - timedelta(weeks=1)
            elif period == AttributionPeriod.MONTHLY:
                start_date = end_date - timedelta(days=30)
            elif period == AttributionPeriod.QUARTERLY:
                start_date = end_date - timedelta(days=90)
            else:  # YEARLY
                start_date = end_date - timedelta(days=365)
            
            # Filter trades for this strategy and period
            strategy_trades = [
                trade for trade in self.trade_history
                if (trade.strategy_name == strategy_name and
                    start_date <= trade.entry_time <= end_date and
                    trade.is_closed)
            ]
            
            if not strategy_trades:
                self.logger.warning(f"No closed trades found for {strategy_name} in {period.value} period")
                return StrategyAttribution(
                    strategy_name=strategy_name,
                    period_start=start_date,
                    period_end=end_date
                )
            
            # Calculate basic metrics
            total_trades = len(strategy_trades)
            winning_trades = len([t for t in strategy_trades if t.actual_pnl > 0])
            losing_trades = len([t for t in strategy_trades if t.actual_pnl < 0])
            total_pnl = sum(t.actual_pnl for t in strategy_trades)
            
            # Calculate performance ratios
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            wins = [t.actual_pnl for t in strategy_trades if t.actual_pnl > 0]
            losses = [abs(t.actual_pnl) for t in strategy_trades if t.actual_pnl < 0]
            
            average_win = statistics.mean(wins) if wins else 0
            average_loss = statistics.mean(losses) if losses else 0
            
            profit_factor = sum(wins) / sum(losses) if losses and sum(losses) > 0 else 0
            
            # Calculate Sharpe ratio
            returns = [t.actual_pnl for t in strategy_trades]
            if len(returns) > 1:
                avg_return = statistics.mean(returns)
                return_std = statistics.stdev(returns)
                sharpe_ratio = (avg_return - self.risk_free_rate/252) / return_std if return_std > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Calculate regime performance
            regime_performance = {}
            volatility_performance = {}
            
            for trade in strategy_trades:
                if trade.entry_regime:
                    regime_key = trade.entry_regime.value
                    if regime_key not in regime_performance:
                        regime_performance[regime_key] = []
                    regime_performance[regime_key].append(trade.actual_pnl)
                
                if trade.entry_volatility:
                    vol_key = trade.entry_volatility.value
                    if vol_key not in volatility_performance:
                        volatility_performance[vol_key] = []
                    volatility_performance[vol_key].append(trade.actual_pnl)
            
            # Aggregate regime performance
            regime_perf_summary = {
                regime: statistics.mean(pnls) 
                for regime, pnls in regime_performance.items()
            }
            vol_perf_summary = {
                vol: statistics.mean(pnls) 
                for vol, pnls in volatility_performance.items()
            }
            
            # Calculate attribution components
            alpha_contribution = self._calculate_alpha_contribution(strategy_trades)
            beta_contribution = self._calculate_beta_contribution(strategy_trades)
            regime_contribution = self._calculate_regime_contribution(strategy_trades)
            timing_contribution = self._calculate_timing_contribution(strategy_trades)
            
            attribution = StrategyAttribution(
                strategy_name=strategy_name,
                period_start=start_date,
                period_end=end_date,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                total_pnl=total_pnl,
                win_rate=win_rate,
                average_win=average_win,
                average_loss=average_loss,
                profit_factor=profit_factor,
                sharpe_ratio=sharpe_ratio,
                regime_performance=regime_perf_summary,
                volatility_performance=vol_perf_summary,
                alpha_contribution=alpha_contribution,
                beta_contribution=beta_contribution,
                regime_contribution=regime_contribution,
                timing_contribution=timing_contribution
            )
            
            self.logger.info(
                "Strategy attribution calculated",
                strategy=strategy_name,
                period=period.value,
                total_pnl=total_pnl,
                win_rate=win_rate,
                sharpe_ratio=sharpe_ratio
            )
            
            return attribution
            
        except Exception as e:
            self.logger.error(f"Strategy attribution calculation failed: {e}")
            return StrategyAttribution(
                strategy_name=strategy_name,
                period_start=start_date,
                period_end=end_date
            )
    
    def calculate_regime_attribution(self, regime: MarketRegime,
                                   period: AttributionPeriod = AttributionPeriod.MONTHLY) -> RegimeAttribution:
        """Calculate performance attribution by market regime"""
        
        try:
            # Get date range
            end_date = datetime.now()
            if period == AttributionPeriod.MONTHLY:
                start_date = end_date - timedelta(days=30)
            elif period == AttributionPeriod.QUARTERLY:
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=365)
            
            # Filter trades in this regime
            regime_trades = [
                trade for trade in self.trade_history
                if (trade.entry_regime == regime and
                    start_date <= trade.entry_time <= end_date and
                    trade.is_closed)
            ]
            
            if not regime_trades:
                return RegimeAttribution(
                    regime=regime,
                    period_start=start_date,
                    period_end=end_date
                )
            
            # Calculate regime metrics
            strategies_used = list(set(t.strategy_name for t in regime_trades))
            total_regime_pnl = sum(t.actual_pnl for t in regime_trades)
            average_regime_pnl = total_regime_pnl / len(regime_trades)
            
            winning_trades = len([t for t in regime_trades if t.actual_pnl > 0])
            regime_win_rate = winning_trades / len(regime_trades)
            
            # Find best/worst strategies in this regime
            strategy_pnls = {}
            for trade in regime_trades:
                strategy = trade.strategy_name
                if strategy not in strategy_pnls:
                    strategy_pnls[strategy] = []
                strategy_pnls[strategy].append(trade.actual_pnl)
            
            strategy_avg_pnls = {
                strategy: statistics.mean(pnls) 
                for strategy, pnls in strategy_pnls.items()
            }
            
            best_strategy = max(strategy_avg_pnls.keys(), key=lambda x: strategy_avg_pnls[x]) if strategy_avg_pnls else None
            worst_strategy = min(strategy_avg_pnls.keys(), key=lambda x: strategy_avg_pnls[x]) if strategy_avg_pnls else None
            
            attribution = RegimeAttribution(
                regime=regime,
                period_start=start_date,
                period_end=end_date,
                strategies_used=strategies_used,
                total_regime_pnl=total_regime_pnl,
                average_regime_pnl=average_regime_pnl,
                regime_win_rate=regime_win_rate,
                best_strategy=best_strategy,
                best_strategy_pnl=strategy_avg_pnls.get(best_strategy, 0) if best_strategy else 0,
                worst_strategy=worst_strategy,
                worst_strategy_pnl=strategy_avg_pnls.get(worst_strategy, 0) if worst_strategy else 0
            )
            
            return attribution
            
        except Exception as e:
            self.logger.error(f"Regime attribution calculation failed: {e}")
            return RegimeAttribution(regime=regime, period_start=start_date, period_end=end_date)
    
    def get_performance_summary(self, period: AttributionPeriod = AttributionPeriod.MONTHLY) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        try:
            # Calculate overall portfolio performance
            end_date = datetime.now()
            if period == AttributionPeriod.MONTHLY:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=90)
            
            recent_trades = [
                trade for trade in self.trade_history
                if start_date <= trade.entry_time <= end_date and trade.is_closed
            ]
            
            if not recent_trades:
                return {"error": "No closed trades in specified period"}
            
            # Overall metrics
            total_pnl = sum(t.actual_pnl for t in recent_trades)
            total_trades = len(recent_trades)
            winning_trades = len([t for t in recent_trades if t.actual_pnl > 0])
            win_rate = winning_trades / total_trades
            
            # Strategy breakdown
            strategy_performance = {}
            strategies = set(t.strategy_name for t in recent_trades)
            
            for strategy in strategies:
                strategy_attribution = self.calculate_strategy_attribution(strategy, period)
                strategy_performance[strategy] = {
                    'total_pnl': strategy_attribution.total_pnl,
                    'win_rate': strategy_attribution.win_rate,
                    'trades': strategy_attribution.total_trades,
                    'sharpe_ratio': strategy_attribution.sharpe_ratio,
                    'profit_factor': strategy_attribution.profit_factor
                }
            
            # Regime breakdown
            regime_performance = {}
            regimes = set(t.entry_regime for t in recent_trades if t.entry_regime)
            
            for regime in regimes:
                regime_attribution = self.calculate_regime_attribution(regime, period)
                regime_performance[regime.value] = {
                    'total_pnl': regime_attribution.total_regime_pnl,
                    'win_rate': regime_attribution.regime_win_rate,
                    'best_strategy': regime_attribution.best_strategy,
                    'strategies_used': len(regime_attribution.strategies_used)
                }
            
            # Top performers
            best_strategy = max(strategy_performance.keys(), 
                              key=lambda x: strategy_performance[x]['total_pnl']) if strategy_performance else None
            worst_strategy = min(strategy_performance.keys(),
                               key=lambda x: strategy_performance[x]['total_pnl']) if strategy_performance else None
            
            summary = {
                'period': period.value,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'overall_performance': {
                    'total_pnl': total_pnl,
                    'total_trades': total_trades,
                    'win_rate': win_rate,
                    'winning_trades': winning_trades,
                    'losing_trades': total_trades - winning_trades
                },
                'strategy_performance': strategy_performance,
                'regime_performance': regime_performance,
                'top_performers': {
                    'best_strategy': best_strategy,
                    'worst_strategy': worst_strategy,
                    'best_strategy_pnl': strategy_performance.get(best_strategy, {}).get('total_pnl', 0) if best_strategy else 0
                },
                'statistics': {
                    'strategies_active': len(strategy_performance),
                    'regimes_encountered': len(regime_performance),
                    'average_trade_pnl': total_pnl / total_trades if total_trades > 0 else 0
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Performance summary calculation failed: {e}")
            return {"error": f"Summary calculation failed: {e}"}
    
    def _calculate_alpha_contribution(self, trades: List[TradePerformance]) -> float:
        """Calculate alpha (strategy skill) contribution"""
        # Simplified alpha calculation - excess return over benchmark
        if not trades:
            return 0.0
        
        strategy_return = sum(t.actual_pnl for t in trades) / len(trades)
        # In real implementation, would compare to market benchmark
        benchmark_return = 0.0  # Placeholder
        alpha = strategy_return - benchmark_return
        
        return alpha * len(trades)  # Total alpha contribution
    
    def _calculate_beta_contribution(self, trades: List[TradePerformance]) -> float:
        """Calculate beta (market direction) contribution"""
        # Simplified beta calculation
        # In real implementation, would calculate correlation with market moves
        return 0.0  # Placeholder
    
    def _calculate_regime_contribution(self, trades: List[TradePerformance]) -> float:
        """Calculate regime selection contribution"""
        if not trades:
            return 0.0
        
        # Calculate performance by regime and weight by regime accuracy
        regime_contributions = []
        
        for trade in trades:
            if trade.entry_regime and trade.entry_confidence > 0:
                # Higher confidence regime selections should contribute more
                regime_weight = trade.entry_confidence
                regime_contribution = trade.actual_pnl * regime_weight
                regime_contributions.append(regime_contribution)
        
        return sum(regime_contributions) if regime_contributions else 0.0
    
    def _calculate_timing_contribution(self, trades: List[TradePerformance]) -> float:
        """Calculate entry/exit timing contribution"""
        # Simplified timing calculation based on hold period vs optimal
        if not trades:
            return 0.0
        
        timing_scores = []
        for trade in trades:
            if trade.days_held > 0:
                # Assuming optimal hold period is related to strategy type
                # This is a simplified calculation
                optimal_days = 7  # Placeholder
                timing_efficiency = min(1.0, optimal_days / trade.days_held)
                timing_contribution = trade.actual_pnl * timing_efficiency
                timing_scores.append(timing_contribution)
        
        return sum(timing_scores) if timing_scores else 0.0