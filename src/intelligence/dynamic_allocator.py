from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import math

from .strategy_selector import StrategyAllocation, AdaptiveStrategySelector
from .market_regime import MarketConditions, VolatilityRegime, TrendStrength
from ..strategies.base_strategy import StrategySignal, MarketData
from ..utils.logger import get_logger


class RiskLevel(Enum):
    """Risk levels for position sizing"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate" 
    AGGRESSIVE = "aggressive"


class AllocationMode(Enum):
    """Allocation modes"""
    EQUAL_WEIGHT = "equal_weight"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    REGIME_ADAPTIVE = "regime_adaptive"
    KELLY_CRITERION = "kelly_criterion"


@dataclass
class PositionAllocation:
    """Individual position allocation"""
    signal: StrategySignal
    position_size: float
    capital_allocation: float
    risk_allocation: float
    max_loss_per_position: float
    reasoning: str


@dataclass
class PortfolioAllocation:
    """Complete portfolio allocation"""
    positions: List[PositionAllocation]
    total_capital_used: float
    total_risk_allocated: float
    expected_return: float
    max_portfolio_loss: float
    allocation_timestamp: datetime
    market_conditions: MarketConditions


class DynamicAllocationManager:
    """Advanced dynamic allocation and position sizing manager"""
    
    def __init__(self, total_capital: float = 1000000, max_risk_per_trade: float = 0.02):
        self.logger = get_logger("dynamic_allocator")
        self.total_capital = total_capital
        self.max_risk_per_trade = max_risk_per_trade  # 2% max risk per trade
        self.max_portfolio_risk = 0.10  # 10% max portfolio risk
        
        # Risk parameters by market regime
        self.regime_risk_adjustments = {
            'bull_trending': {'risk_multiplier': 1.2, 'max_positions': 8},
            'bear_trending': {'risk_multiplier': 0.8, 'max_positions': 6},
            'bull_volatile': {'risk_multiplier': 0.9, 'max_positions': 5},
            'bear_volatile': {'risk_multiplier': 0.7, 'max_positions': 4},
            'sideways_low_vol': {'risk_multiplier': 1.1, 'max_positions': 10},
            'sideways_high_vol': {'risk_multiplier': 0.9, 'max_positions': 6},
            'breakout_pending': {'risk_multiplier': 0.8, 'max_positions': 5},
            'high_uncertainty': {'risk_multiplier': 0.6, 'max_positions': 3}
        }
        
        # Current positions tracking
        self.current_positions: List[PositionAllocation] = []
        self.total_allocated_capital = 0.0
        self.total_allocated_risk = 0.0
    
    def allocate_portfolio(self, signals: List[StrategySignal], market_conditions: MarketConditions,
                          allocation_mode: AllocationMode = AllocationMode.REGIME_ADAPTIVE) -> PortfolioAllocation:
        """Create optimal portfolio allocation from signals"""
        
        if not signals:
            return PortfolioAllocation(
                positions=[], total_capital_used=0, total_risk_allocated=0,
                expected_return=0, max_portfolio_loss=0, 
                allocation_timestamp=datetime.now(), market_conditions=market_conditions
            )
        
        # Filter signals based on current portfolio
        available_signals = self._filter_available_signals(signals, market_conditions)
        
        if not available_signals:
            self.logger.info("No new signals available for allocation")
            return self._create_empty_allocation(market_conditions)
        
        # Calculate position allocations
        if allocation_mode == AllocationMode.EQUAL_WEIGHT:
            positions = self._allocate_equal_weight(available_signals, market_conditions)
        elif allocation_mode == AllocationMode.CONFIDENCE_WEIGHTED:
            positions = self._allocate_confidence_weighted(available_signals, market_conditions)
        elif allocation_mode == AllocationMode.KELLY_CRITERION:
            positions = self._allocate_kelly_criterion(available_signals, market_conditions)
        else:  # REGIME_ADAPTIVE
            positions = self._allocate_regime_adaptive(available_signals, market_conditions)
        
        # Calculate portfolio metrics
        total_capital_used = sum(pos.capital_allocation for pos in positions)
        total_risk_allocated = sum(pos.risk_allocation for pos in positions)
        expected_return = sum(pos.signal.max_profit * pos.position_size for pos in positions)
        max_portfolio_loss = sum(pos.max_loss_per_position for pos in positions)
        
        allocation = PortfolioAllocation(
            positions=positions,
            total_capital_used=total_capital_used,
            total_risk_allocated=total_risk_allocated,
            expected_return=expected_return,
            max_portfolio_loss=max_portfolio_loss,
            allocation_timestamp=datetime.now(),
            market_conditions=market_conditions
        )
        
        self.logger.info(
            "Portfolio allocation completed",
            positions=len(positions),
            capital_used=total_capital_used,
            risk_allocated=total_risk_allocated,
            expected_return=expected_return
        )
        
        return allocation
    
    def _filter_available_signals(self, signals: List[StrategySignal], 
                                 market_conditions: MarketConditions) -> List[StrategySignal]:
        """Filter signals based on current portfolio and risk limits"""
        
        available_signals = []
        regime = market_conditions.regime.value
        regime_config = self.regime_risk_adjustments.get(regime, {'max_positions': 5})
        max_positions = regime_config['max_positions']
        
        # Check portfolio limits
        if len(self.current_positions) >= max_positions:
            self.logger.info(f"Portfolio at max positions ({max_positions}) for {regime} regime")
            return []
        
        remaining_positions = max_positions - len(self.current_positions)
        
        # Sort signals by confidence and take top candidates
        sorted_signals = sorted(signals, key=lambda x: x.confidence_score, reverse=True)
        
        for signal in sorted_signals[:remaining_positions * 2]:  # Consider 2x candidates
            # Skip if risk would be too high
            estimated_risk = self._estimate_position_risk(signal, market_conditions)
            if self.total_allocated_risk + estimated_risk > self.max_portfolio_risk:
                continue
            
            # Skip if similar position already exists
            if self._has_similar_position(signal):
                continue
            
            available_signals.append(signal)
            
            if len(available_signals) >= remaining_positions:
                break
        
        return available_signals
    
    def _allocate_regime_adaptive(self, signals: List[StrategySignal], 
                                 market_conditions: MarketConditions) -> List[PositionAllocation]:
        """Regime-adaptive allocation strategy"""
        
        positions = []
        regime = market_conditions.regime.value
        regime_config = self.regime_risk_adjustments.get(regime, {'risk_multiplier': 1.0})
        
        base_risk_per_trade = self.max_risk_per_trade * regime_config['risk_multiplier']
        
        # Adjust risk based on market conditions
        volatility_adjustment = self._get_volatility_risk_adjustment(market_conditions.volatility_regime)
        confidence_adjustment = market_conditions.confidence_score
        
        for signal in signals:
            # Calculate position-specific risk
            position_risk = base_risk_per_trade * volatility_adjustment * confidence_adjustment
            position_risk = min(position_risk, self.max_risk_per_trade * 1.5)  # Cap at 3%
            
            # Calculate position size
            max_loss_per_contract = abs(signal.max_loss)
            if max_loss_per_contract > 0:
                max_capital_risk = self.total_capital * position_risk
                position_size = math.floor(max_capital_risk / max_loss_per_contract)
                position_size = max(1, position_size)  # At least 1 contract
            else:
                position_size = 1
            
            # Calculate allocations
            capital_allocation = position_size * abs(signal.max_loss)
            risk_allocation = capital_allocation / self.total_capital
            max_loss_per_position = position_size * abs(signal.max_loss)
            
            reasoning = (f"Regime: {regime}, Risk Adj: {regime_config['risk_multiplier']:.1f}, "
                        f"Vol Adj: {volatility_adjustment:.1f}, Conf: {confidence_adjustment:.1%}")
            
            positions.append(PositionAllocation(
                signal=signal,
                position_size=position_size,
                capital_allocation=capital_allocation,
                risk_allocation=risk_allocation,
                max_loss_per_position=max_loss_per_position,
                reasoning=reasoning
            ))
        
        return positions
    
    def _allocate_confidence_weighted(self, signals: List[StrategySignal], 
                                    market_conditions: MarketConditions) -> List[PositionAllocation]:
        """Confidence-weighted allocation strategy"""
        
        positions = []
        total_confidence = sum(signal.confidence_score for signal in signals)
        
        if total_confidence == 0:
            return self._allocate_equal_weight(signals, market_conditions)
        
        for signal in signals:
            # Weight by confidence
            confidence_weight = signal.confidence_score / total_confidence
            position_risk = self.max_risk_per_trade * confidence_weight * len(signals)
            position_risk = min(position_risk, self.max_risk_per_trade * 1.5)
            
            # Calculate position size
            max_loss_per_contract = abs(signal.max_loss)
            if max_loss_per_contract > 0:
                max_capital_risk = self.total_capital * position_risk
                position_size = math.floor(max_capital_risk / max_loss_per_contract)
                position_size = max(1, position_size)
            else:
                position_size = 1
            
            capital_allocation = position_size * abs(signal.max_loss)
            risk_allocation = capital_allocation / self.total_capital
            max_loss_per_position = position_size * abs(signal.max_loss)
            
            reasoning = f"Confidence weighted: {signal.confidence_score:.1%} of total"
            
            positions.append(PositionAllocation(
                signal=signal,
                position_size=position_size,
                capital_allocation=capital_allocation,
                risk_allocation=risk_allocation,
                max_loss_per_position=max_loss_per_position,
                reasoning=reasoning
            ))
        
        return positions
    
    def _allocate_equal_weight(self, signals: List[StrategySignal], 
                             market_conditions: MarketConditions) -> List[PositionAllocation]:
        """Equal weight allocation strategy"""
        
        positions = []
        equal_risk = self.max_risk_per_trade
        
        for signal in signals:
            max_loss_per_contract = abs(signal.max_loss)
            if max_loss_per_contract > 0:
                max_capital_risk = self.total_capital * equal_risk
                position_size = math.floor(max_capital_risk / max_loss_per_contract)
                position_size = max(1, position_size)
            else:
                position_size = 1
            
            capital_allocation = position_size * abs(signal.max_loss)
            risk_allocation = capital_allocation / self.total_capital
            max_loss_per_position = position_size * abs(signal.max_loss)
            
            reasoning = f"Equal weight allocation: {equal_risk:.1%} risk per position"
            
            positions.append(PositionAllocation(
                signal=signal,
                position_size=position_size,
                capital_allocation=capital_allocation,
                risk_allocation=risk_allocation,
                max_loss_per_position=max_loss_per_position,
                reasoning=reasoning
            ))
        
        return positions
    
    def _allocate_kelly_criterion(self, signals: List[StrategySignal], 
                                 market_conditions: MarketConditions) -> List[PositionAllocation]:
        """Kelly criterion allocation strategy"""
        
        positions = []
        
        for signal in signals:
            # Kelly formula: f = (bp - q) / b
            # where b = odds, p = win probability, q = lose probability
            
            win_prob = signal.probability_of_profit
            lose_prob = 1 - win_prob
            
            if signal.max_loss != 0:
                odds = signal.max_profit / abs(signal.max_loss)
                kelly_fraction = (odds * win_prob - lose_prob) / odds
                
                # Apply Kelly fraction with safety limits
                kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
                position_risk = kelly_fraction
            else:
                position_risk = self.max_risk_per_trade
            
            # Calculate position size
            max_loss_per_contract = abs(signal.max_loss)
            if max_loss_per_contract > 0:
                max_capital_risk = self.total_capital * position_risk
                position_size = math.floor(max_capital_risk / max_loss_per_contract)
                position_size = max(1, position_size)
            else:
                position_size = 1
            
            capital_allocation = position_size * abs(signal.max_loss)
            risk_allocation = capital_allocation / self.total_capital
            max_loss_per_position = position_size * abs(signal.max_loss)
            
            reasoning = f"Kelly criterion: {kelly_fraction:.1%} optimal fraction"
            
            positions.append(PositionAllocation(
                signal=signal,
                position_size=position_size,
                capital_allocation=capital_allocation,
                risk_allocation=risk_allocation,
                max_loss_per_position=max_loss_per_position,
                reasoning=reasoning
            ))
        
        return positions
    
    def _get_volatility_risk_adjustment(self, volatility_regime: VolatilityRegime) -> float:
        """Get risk adjustment based on volatility regime"""
        if volatility_regime == VolatilityRegime.EXTREME:
            return 0.7  # Reduce risk in extreme volatility
        elif volatility_regime == VolatilityRegime.HIGH:
            return 0.85
        elif volatility_regime == VolatilityRegime.LOW:
            return 1.1  # Increase risk in low volatility
        else:  # MEDIUM
            return 1.0
    
    def _estimate_position_risk(self, signal: StrategySignal, market_conditions: MarketConditions) -> float:
        """Estimate the risk of a position as percentage of total capital"""
        max_loss_per_contract = abs(signal.max_loss)
        estimated_position_size = 1  # Conservative estimate
        estimated_max_loss = max_loss_per_contract * estimated_position_size
        return estimated_max_loss / self.total_capital
    
    def _has_similar_position(self, signal: StrategySignal) -> bool:
        """Check if similar position already exists in portfolio"""
        for pos in self.current_positions:
            # Same strategy and similar confidence
            if (pos.signal.strategy_name == signal.strategy_name and 
                abs(pos.signal.confidence_score - signal.confidence_score) < 0.1):
                return True
        return False
    
    def _create_empty_allocation(self, market_conditions: MarketConditions) -> PortfolioAllocation:
        """Create empty portfolio allocation"""
        return PortfolioAllocation(
            positions=[],
            total_capital_used=0,
            total_risk_allocated=0,
            expected_return=0,
            max_portfolio_loss=0,
            allocation_timestamp=datetime.now(),
            market_conditions=market_conditions
        )
    
    def update_positions(self, allocation: PortfolioAllocation):
        """Update current positions tracking"""
        self.current_positions = allocation.positions
        self.total_allocated_capital = allocation.total_capital_used
        self.total_allocated_risk = allocation.total_risk_allocated
        
        self.logger.info(
            "Position tracking updated",
            positions=len(self.current_positions),
            capital_used=self.total_allocated_capital,
            risk_allocated=self.total_allocated_risk
        )
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        return {
            'total_positions': len(self.current_positions),
            'total_capital': self.total_capital,
            'allocated_capital': self.total_allocated_capital,
            'available_capital': self.total_capital - self.total_allocated_capital,
            'allocated_risk': self.total_allocated_risk,
            'available_risk': self.max_portfolio_risk - self.total_allocated_risk,
            'utilization': {
                'capital': self.total_allocated_capital / self.total_capital,
                'risk': self.total_allocated_risk / self.max_portfolio_risk
            }
        }