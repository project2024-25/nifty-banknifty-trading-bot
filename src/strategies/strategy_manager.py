from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from .base_strategy import BaseStrategy, StrategySignal, MarketData
from .iron_condor import IronCondorStrategy
from .conservative.bull_put_spread import BullPutSpreadStrategy
from .conservative.bear_call_spread import BearCallSpreadStrategy
from .conservative.bull_call_spread import BullCallSpreadStrategy
from .conservative.bear_put_spread import BearPutSpreadStrategy
from .conservative.butterfly_spread import ButterflySpreadStrategy
from .conservative.covered_call import CoveredCallStrategy
from .aggressive.long_straddle import LongStraddleStrategy
from .aggressive.short_straddle import ShortStraddleStrategy
from .aggressive.long_strangle import LongStrangleStrategy
from .aggressive.short_strangle import ShortStrangleStrategy
from ..utils.logger import get_logger


class StrategyManager:
    def __init__(self):
        self.logger = get_logger("strategy_manager")
        self.strategies: Dict[str, BaseStrategy] = {}
        self.active_signals: List[StrategySignal] = []
        self.strategy_performance: Dict[str, Dict] = {}
        
        # Risk management parameters
        self.max_correlation_threshold = 0.7
        self.max_daily_signals = 5
        self.min_signal_gap_minutes = 30
        
        # Initialize strategies
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        # Add Iron Condor strategy
        iron_condor = IronCondorStrategy()
        self.strategies[iron_condor.name] = iron_condor
        
        # Add Conservative strategies
        bull_put_spread = BullPutSpreadStrategy()
        self.strategies[bull_put_spread.name] = bull_put_spread
        
        bear_call_spread = BearCallSpreadStrategy()
        self.strategies[bear_call_spread.name] = bear_call_spread
        
        bull_call_spread = BullCallSpreadStrategy()
        self.strategies[bull_call_spread.name] = bull_call_spread
        
        bear_put_spread = BearPutSpreadStrategy()
        self.strategies[bear_put_spread.name] = bear_put_spread
        
        butterfly_spread = ButterflySpreadStrategy()
        self.strategies[butterfly_spread.name] = butterfly_spread
        
        covered_call = CoveredCallStrategy()
        self.strategies[covered_call.name] = covered_call
        
        # Add Aggressive strategies
        long_straddle = LongStraddleStrategy()
        self.strategies[long_straddle.name] = long_straddle
        
        short_straddle = ShortStraddleStrategy()
        self.strategies[short_straddle.name] = short_straddle
        
        long_strangle = LongStrangleStrategy()
        self.strategies[long_strangle.name] = long_strangle
        
        short_strangle = ShortStrangleStrategy()
        self.strategies[short_strangle.name] = short_strangle
        
        # Initialize performance tracking
        for strategy_name in self.strategies:
            self.strategy_performance[strategy_name] = {
                "total_signals": 0,
                "successful_signals": 0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "last_signal_time": None
            }
        
        self.logger.info("Strategy manager initialized", strategies=list(self.strategies.keys()))
    
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        all_signals = []
        
        for strategy_name, strategy in self.strategies.items():
            if not strategy.is_active:
                continue
                
            try:
                # Generate signals from strategy
                strategy_signals = await strategy.generate_signals(market_data)
                
                # Validate and filter signals
                for signal in strategy_signals:
                    if self._validate_signal_with_risk_checks(signal, strategy):
                        all_signals.append(signal)
                        self.logger.info(
                            "Signal generated",
                            strategy=strategy_name,
                            symbol=signal.symbol,
                            confidence=signal.confidence_score,
                            max_profit=signal.max_profit,
                            max_loss=signal.max_loss
                        )
                    else:
                        self.logger.warning(
                            "Signal rejected by risk checks",
                            strategy=strategy_name,
                            symbol=signal.symbol,
                            confidence=signal.confidence_score
                        )
                        
            except Exception as e:
                self.logger.error(
                    "Error generating signals",
                    strategy=strategy_name,
                    error=str(e)
                )
        
        # Apply portfolio-level risk management
        filtered_signals = self._apply_portfolio_risk_management(all_signals)
        
        # Update active signals
        self.active_signals.extend(filtered_signals)
        
        return filtered_signals
    
    def _validate_signal_with_risk_checks(self, signal: StrategySignal, strategy: BaseStrategy) -> bool:
        # Basic strategy validation
        current_positions = len([s for s in self.active_signals if s.symbol == signal.symbol])
        
        if not strategy.validate_signal(signal, current_positions):
            return False
        
        # Time-based validation
        if not self._check_signal_timing(strategy.name):
            return False
        
        # Correlation checks
        if not self._check_correlation_risk(signal):
            return False
        
        # Daily signal limit
        if not self._check_daily_signal_limit():
            return False
        
        return True
    
    def _check_signal_timing(self, strategy_name: str) -> bool:
        last_signal_time = self.strategy_performance[strategy_name]["last_signal_time"]
        
        if last_signal_time is None:
            return True
        
        time_since_last = (datetime.now() - last_signal_time).total_seconds() / 60
        return time_since_last >= self.min_signal_gap_minutes
    
    def _check_correlation_risk(self, new_signal: StrategySignal) -> bool:
        # Check correlation with existing signals
        for existing_signal in self.active_signals:
            if existing_signal.symbol == new_signal.symbol:
                # Same underlying - high correlation
                return False
            
            # Check for similar strategy structures
            if self._calculate_strategy_correlation(new_signal, existing_signal) > self.max_correlation_threshold:
                return False
        
        return True
    
    def _calculate_strategy_correlation(self, signal1: StrategySignal, signal2: StrategySignal) -> float:
        # Simplified correlation calculation based on strategy similarity
        
        # Same strategy type = high correlation
        if signal1.strategy_name == signal2.strategy_name:
            return 0.8
        
        # Both Iron Condors on related indices (NIFTY/BANKNIFTY)
        if (signal1.strategy_name == "Iron Condor" and signal2.strategy_name == "Iron Condor" and
            set([signal1.symbol, signal2.symbol]) == set(["NIFTY", "BANKNIFTY"])):
            return 0.6
        
        # Different strategies on same underlying
        if signal1.symbol == signal2.symbol:
            return 0.7
        
        return 0.2  # Low correlation for different strategies/underlyings
    
    def _check_daily_signal_limit(self) -> bool:
        today_signals = [
            s for s in self.active_signals 
            if s.generated_at.date() == datetime.now().date()
        ]
        return len(today_signals) < self.max_daily_signals
    
    def _apply_portfolio_risk_management(self, signals: List[StrategySignal]) -> List[StrategySignal]:
        # Sort signals by confidence score (descending)
        signals.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Apply position concentration limits
        filtered_signals = []
        symbol_count = {}
        
        for signal in signals:
            # Limit positions per symbol
            current_symbol_positions = symbol_count.get(signal.symbol, 0)
            if current_symbol_positions >= 2:  # Max 2 positions per underlying
                continue
            
            # Check total portfolio risk
            total_max_loss = sum(s.max_loss for s in filtered_signals)
            if total_max_loss + signal.max_loss > 50000:  # Max 50k total risk
                continue
            
            filtered_signals.append(signal)
            symbol_count[signal.symbol] = current_symbol_positions + 1
        
        return filtered_signals
    
    def update_signal_performance(self, signal_id: str, pnl: float, is_closed: bool):
        # Find the signal and update performance
        for signal in self.active_signals:
            if hasattr(signal, 'id') and signal.id == signal_id:
                strategy_name = signal.strategy_name
                perf = self.strategy_performance[strategy_name]
                
                if is_closed:
                    perf["total_pnl"] += pnl
                    perf["successful_signals"] += 1 if pnl > 0 else 0
                    perf["win_rate"] = perf["successful_signals"] / max(perf["total_signals"], 1)
                    
                    # Remove from active signals
                    self.active_signals.remove(signal)
                    
                self.logger.info(
                    "Signal performance updated",
                    strategy=strategy_name,
                    pnl=pnl,
                    is_closed=is_closed,
                    win_rate=perf["win_rate"]
                )
                break
    
    def get_strategy_performance(self) -> Dict[str, Any]:
        return {
            "strategies": self.strategy_performance,
            "active_signals_count": len(self.active_signals),
            "total_portfolio_risk": sum(s.max_loss for s in self.active_signals)
        }
    
    def get_active_strategies(self) -> List[str]:
        return [name for name, strategy in self.strategies.items() if strategy.is_active]
    
    def enable_strategy(self, strategy_name: str) -> bool:
        if strategy_name in self.strategies:
            self.strategies[strategy_name].is_active = True
            self.logger.info("Strategy enabled", strategy=strategy_name)
            return True
        return False
    
    def disable_strategy(self, strategy_name: str) -> bool:
        if strategy_name in self.strategies:
            self.strategies[strategy_name].is_active = False
            self.logger.info("Strategy disabled", strategy=strategy_name)
            return True
        return False