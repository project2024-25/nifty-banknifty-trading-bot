from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

from .market_regime import MarketRegimeDetector, MarketRegime, VolatilityRegime, TrendStrength, MarketConditions
from ..strategies.base_strategy import MarketData, StrategySignal, StrategyType
from ..utils.logger import get_logger

# Import all strategies
from ..strategies.iron_condor import IronCondorStrategy
from ..strategies.conservative.bull_put_spread import BullPutSpreadStrategy
from ..strategies.conservative.bear_call_spread import BearCallSpreadStrategy
from ..strategies.conservative.bull_call_spread import BullCallSpreadStrategy
from ..strategies.conservative.bear_put_spread import BearPutSpreadStrategy
from ..strategies.conservative.butterfly_spread import ButterflySpreadStrategy
from ..strategies.conservative.covered_call import CoveredCallStrategy
from ..strategies.aggressive.long_straddle import LongStraddleStrategy
from ..strategies.aggressive.short_straddle import ShortStraddleStrategy
from ..strategies.aggressive.long_strangle import LongStrangleStrategy
from ..strategies.aggressive.short_strangle import ShortStrangleStrategy


class StrategyPreference(Enum):
    """Strategy preference levels"""
    HIGHLY_PREFERRED = "highly_preferred"
    PREFERRED = "preferred"
    NEUTRAL = "neutral"
    DISCOURAGED = "discouraged"
    AVOIDED = "avoided"


@dataclass
class StrategyRecommendation:
    """Strategy recommendation with reasoning"""
    strategy_name: str
    preference: StrategyPreference
    weight: float  # 0.0 to 1.0
    reasoning: str
    confidence: float


@dataclass
class StrategyAllocation:
    """Final strategy allocation"""
    strategy_name: str
    allocation_weight: float
    max_positions: int
    priority: int


class AdaptiveStrategySelector:
    """Intelligent strategy selection based on market regime"""
    
    def __init__(self):
        self.logger = get_logger("strategy_selector")
        self.regime_detector = MarketRegimeDetector()
        
        # Initialize all strategies
        self.strategies = {
            'iron_condor': IronCondorStrategy(),
            'bull_put_spread': BullPutSpreadStrategy(),
            'bear_call_spread': BearCallSpreadStrategy(),
            'bull_call_spread': BullCallSpreadStrategy(),
            'bear_put_spread': BearPutSpreadStrategy(),
            'butterfly_spread': ButterflySpreadStrategy(),
            'covered_call': CoveredCallStrategy(),
            'long_straddle': LongStraddleStrategy(),
            'short_straddle': ShortStraddleStrategy(),
            'long_strangle': LongStrangleStrategy(),
            'short_strangle': ShortStrangleStrategy(),
        }
        
        # Define strategy-regime compatibility matrix
        self.regime_strategy_matrix = {
            MarketRegime.BULL_TRENDING: {
                'bull_call_spread': StrategyPreference.HIGHLY_PREFERRED,
                'bull_put_spread': StrategyPreference.PREFERRED,
                'covered_call': StrategyPreference.PREFERRED,
                'bear_call_spread': StrategyPreference.DISCOURAGED,
                'bear_put_spread': StrategyPreference.AVOIDED,
                'long_straddle': StrategyPreference.DISCOURAGED,
                'short_straddle': StrategyPreference.NEUTRAL,
                'long_strangle': StrategyPreference.DISCOURAGED,
                'short_strangle': StrategyPreference.NEUTRAL,
                'butterfly_spread': StrategyPreference.NEUTRAL,
                'iron_condor': StrategyPreference.DISCOURAGED
            },
            
            MarketRegime.BEAR_TRENDING: {
                'bear_put_spread': StrategyPreference.HIGHLY_PREFERRED,
                'bear_call_spread': StrategyPreference.PREFERRED,
                'bull_call_spread': StrategyPreference.AVOIDED,
                'bull_put_spread': StrategyPreference.DISCOURAGED,
                'covered_call': StrategyPreference.AVOIDED,
                'long_straddle': StrategyPreference.DISCOURAGED,
                'short_straddle': StrategyPreference.NEUTRAL,
                'long_strangle': StrategyPreference.DISCOURAGED,
                'short_strangle': StrategyPreference.NEUTRAL,
                'butterfly_spread': StrategyPreference.NEUTRAL,
                'iron_condor': StrategyPreference.DISCOURAGED
            },
            
            MarketRegime.BULL_VOLATILE: {
                'long_straddle': StrategyPreference.PREFERRED,
                'long_strangle': StrategyPreference.PREFERRED,
                'bull_call_spread': StrategyPreference.NEUTRAL,
                'bull_put_spread': StrategyPreference.DISCOURAGED,
                'short_straddle': StrategyPreference.AVOIDED,
                'short_strangle': StrategyPreference.DISCOURAGED,
                'butterfly_spread': StrategyPreference.DISCOURAGED,
                'iron_condor': StrategyPreference.AVOIDED,
                'bear_call_spread': StrategyPreference.DISCOURAGED,
                'bear_put_spread': StrategyPreference.AVOIDED,
                'covered_call': StrategyPreference.NEUTRAL
            },
            
            MarketRegime.BEAR_VOLATILE: {
                'long_straddle': StrategyPreference.PREFERRED,
                'long_strangle': StrategyPreference.PREFERRED,
                'bear_put_spread': StrategyPreference.NEUTRAL,
                'bear_call_spread': StrategyPreference.DISCOURAGED,
                'short_straddle': StrategyPreference.AVOIDED,
                'short_strangle': StrategyPreference.DISCOURAGED,
                'butterfly_spread': StrategyPreference.DISCOURAGED,
                'iron_condor': StrategyPreference.AVOIDED,
                'bull_call_spread': StrategyPreference.AVOIDED,
                'bull_put_spread': StrategyPreference.DISCOURAGED,
                'covered_call': StrategyPreference.AVOIDED
            },
            
            MarketRegime.SIDEWAYS_LOW_VOL: {
                'iron_condor': StrategyPreference.HIGHLY_PREFERRED,
                'butterfly_spread': StrategyPreference.PREFERRED,
                'short_straddle': StrategyPreference.PREFERRED,
                'short_strangle': StrategyPreference.PREFERRED,
                'bull_put_spread': StrategyPreference.NEUTRAL,
                'bear_call_spread': StrategyPreference.NEUTRAL,
                'covered_call': StrategyPreference.NEUTRAL,
                'long_straddle': StrategyPreference.AVOIDED,
                'long_strangle': StrategyPreference.DISCOURAGED,
                'bull_call_spread': StrategyPreference.DISCOURAGED,
                'bear_put_spread': StrategyPreference.DISCOURAGED
            },
            
            MarketRegime.SIDEWAYS_HIGH_VOL: {
                'short_straddle': StrategyPreference.HIGHLY_PREFERRED,
                'short_strangle': StrategyPreference.PREFERRED,
                'iron_condor': StrategyPreference.PREFERRED,
                'butterfly_spread': StrategyPreference.NEUTRAL,
                'bull_put_spread': StrategyPreference.NEUTRAL,
                'bear_call_spread': StrategyPreference.NEUTRAL,
                'long_straddle': StrategyPreference.DISCOURAGED,
                'long_strangle': StrategyPreference.DISCOURAGED,
                'bull_call_spread': StrategyPreference.DISCOURAGED,
                'bear_put_spread': StrategyPreference.DISCOURAGED,
                'covered_call': StrategyPreference.NEUTRAL
            },
            
            MarketRegime.BREAKOUT_PENDING: {
                'long_straddle': StrategyPreference.HIGHLY_PREFERRED,
                'long_strangle': StrategyPreference.PREFERRED,
                'short_straddle': StrategyPreference.AVOIDED,
                'short_strangle': StrategyPreference.DISCOURAGED,
                'iron_condor': StrategyPreference.DISCOURAGED,
                'butterfly_spread': StrategyPreference.DISCOURAGED,
                'bull_call_spread': StrategyPreference.NEUTRAL,
                'bear_put_spread': StrategyPreference.NEUTRAL,
                'bull_put_spread': StrategyPreference.NEUTRAL,
                'bear_call_spread': StrategyPreference.NEUTRAL,
                'covered_call': StrategyPreference.NEUTRAL
            },
            
            MarketRegime.HIGH_UNCERTAINTY: {
                'butterfly_spread': StrategyPreference.PREFERRED,
                'iron_condor': StrategyPreference.NEUTRAL,
                'short_straddle': StrategyPreference.NEUTRAL,
                'short_strangle': StrategyPreference.NEUTRAL,
                'long_straddle': StrategyPreference.DISCOURAGED,
                'long_strangle': StrategyPreference.DISCOURAGED,
                'bull_call_spread': StrategyPreference.DISCOURAGED,
                'bear_put_spread': StrategyPreference.DISCOURAGED,
                'bull_put_spread': StrategyPreference.DISCOURAGED,
                'bear_call_spread': StrategyPreference.DISCOURAGED,
                'covered_call': StrategyPreference.DISCOURAGED
            }
        }
        
        # Preference weights
        self.preference_weights = {
            StrategyPreference.HIGHLY_PREFERRED: 1.0,
            StrategyPreference.PREFERRED: 0.8,
            StrategyPreference.NEUTRAL: 0.5,
            StrategyPreference.DISCOURAGED: 0.2,
            StrategyPreference.AVOIDED: 0.05
        }
    
    async def select_strategies(self, market_data: MarketData) -> List[StrategyAllocation]:
        """Select optimal strategies based on current market regime"""
        
        # Detect current market regime
        market_conditions = self.regime_detector.detect_regime(market_data)
        
        self.logger.info(
            "Analyzing market for strategy selection",
            regime=market_conditions.regime.value,
            volatility=market_conditions.volatility_regime.value,
            trend=market_conditions.trend_direction,
            confidence=market_conditions.confidence_score
        )
        
        # Get strategy recommendations
        recommendations = self._get_strategy_recommendations(market_conditions)
        
        # Filter strategies based on market conditions
        viable_strategies = await self._filter_viable_strategies(market_data, recommendations)
        
        # Calculate final allocations
        allocations = self._calculate_strategy_allocations(viable_strategies, market_conditions)
        
        self.logger.info(
            f"Strategy selection complete",
            selected_strategies=len(allocations),
            top_strategy=allocations[0].strategy_name if allocations else "none"
        )
        
        return allocations
    
    def _get_strategy_recommendations(self, conditions: MarketConditions) -> List[StrategyRecommendation]:
        """Get strategy recommendations based on market regime"""
        recommendations = []
        
        # Get base recommendations from regime matrix
        regime_preferences = self.regime_strategy_matrix.get(conditions.regime, {})
        
        for strategy_name, preference in regime_preferences.items():
            base_weight = self.preference_weights[preference]
            
            # Adjust weight based on additional market factors
            adjusted_weight = self._adjust_strategy_weight(
                strategy_name, base_weight, conditions
            )
            
            # Generate reasoning
            reasoning = self._generate_strategy_reasoning(
                strategy_name, preference, conditions
            )
            
            recommendations.append(StrategyRecommendation(
                strategy_name=strategy_name,
                preference=preference,
                weight=adjusted_weight,
                reasoning=reasoning,
                confidence=conditions.confidence_score
            ))
        
        # Sort by adjusted weight
        recommendations.sort(key=lambda x: x.weight, reverse=True)
        
        return recommendations
    
    def _adjust_strategy_weight(self, strategy_name: str, base_weight: float, 
                              conditions: MarketConditions) -> float:
        """Adjust strategy weight based on additional market factors"""
        
        weight = base_weight
        
        # IV-based adjustments
        if conditions.volatility_regime == VolatilityRegime.EXTREME:
            # Premium selling strategies benefit from extreme IV
            if strategy_name in ['short_straddle', 'short_strangle', 'iron_condor', 
                               'bull_put_spread', 'bear_call_spread']:
                weight *= 1.3
            # Premium buying strategies suffer
            elif strategy_name in ['long_straddle', 'long_strangle']:
                weight *= 0.7
        
        elif conditions.volatility_regime == VolatilityRegime.LOW:
            # Premium buying strategies benefit from low IV
            if strategy_name in ['long_straddle', 'long_strangle', 'bull_call_spread', 'bear_put_spread']:
                weight *= 1.2
            # Premium selling strategies less attractive
            elif strategy_name in ['short_straddle', 'short_strangle']:
                weight *= 0.8
        
        # Trend strength adjustments
        if conditions.trend_strength == TrendStrength.STRONG:
            # Directional strategies benefit
            if strategy_name in ['bull_call_spread', 'bear_put_spread'] and conditions.trend_direction == 'bullish':
                weight *= 1.4
            elif strategy_name in ['bear_call_spread', 'bull_put_spread'] and conditions.trend_direction == 'bearish':
                weight *= 1.4
            # Range-bound strategies suffer
            elif strategy_name in ['iron_condor', 'butterfly_spread', 'short_straddle']:
                weight *= 0.6
        
        # Momentum-based adjustments
        if abs(conditions.momentum_score) > 0.7:
            # Strong momentum favors long options in breakout direction
            if conditions.momentum_score > 0.7 and strategy_name in ['bull_call_spread', 'long_straddle']:
                weight *= 1.2
            elif conditions.momentum_score < -0.7 and strategy_name in ['bear_put_spread', 'long_straddle']:
                weight *= 1.2
        
        # Mean reversion adjustments
        if conditions.mean_reversion_likelihood > 0.7:
            # High mean reversion probability favors range-bound strategies
            if strategy_name in ['iron_condor', 'butterfly_spread', 'short_straddle', 'short_strangle']:
                weight *= 1.3
            # Discourages trend-following strategies
            elif strategy_name in ['bull_call_spread', 'bear_put_spread']:
                weight *= 0.7
        
        # Breakout probability adjustments
        if conditions.breakout_probability > 0.7:
            # High breakout probability favors long volatility strategies
            if strategy_name in ['long_straddle', 'long_strangle']:
                weight *= 1.4
            # Discourages short volatility strategies
            elif strategy_name in ['short_straddle', 'short_strangle', 'iron_condor']:
                weight *= 0.6
        
        # Confidence-based adjustment
        weight *= conditions.confidence_score
        
        return max(0.0, min(1.0, weight))
    
    def _generate_strategy_reasoning(self, strategy_name: str, preference: StrategyPreference,
                                   conditions: MarketConditions) -> str:
        """Generate human-readable reasoning for strategy recommendation"""
        
        regime = conditions.regime.value.replace('_', ' ').title()
        vol_regime = conditions.volatility_regime.value
        trend = conditions.trend_direction
        
        base_reason = f"{regime} market with {vol_regime} volatility and {trend} trend"
        
        if preference == StrategyPreference.HIGHLY_PREFERRED:
            return f"Optimal for {base_reason}. High probability of success."
        elif preference == StrategyPreference.PREFERRED:
            return f"Well-suited for {base_reason}. Good risk-reward profile."
        elif preference == StrategyPreference.NEUTRAL:
            return f"Acceptable for {base_reason}. Monitor closely."
        elif preference == StrategyPreference.DISCOURAGED:
            return f"Less suitable for {base_reason}. Consider alternatives."
        else:  # AVOIDED
            return f"Poor fit for {base_reason}. High risk of loss."
    
    async def _filter_viable_strategies(self, market_data: MarketData, 
                                       recommendations: List[StrategyRecommendation]) -> List[StrategyRecommendation]:
        """Filter strategies that can actually generate signals"""
        
        viable_strategies = []
        
        for rec in recommendations:
            if rec.weight < 0.1:  # Skip very low weight strategies
                continue
                
            strategy = self.strategies.get(rec.strategy_name)
            if not strategy:
                continue
            
            try:
                # Test if strategy can generate a signal
                signals = await strategy.generate_signals(market_data)
                if signals:
                    # Strategy is viable
                    viable_strategies.append(rec)
                    self.logger.debug(f"Strategy {rec.strategy_name} is viable")
                else:
                    self.logger.debug(f"Strategy {rec.strategy_name} cannot generate signals")
            
            except Exception as e:
                self.logger.warning(f"Error testing strategy {rec.strategy_name}: {e}")
        
        return viable_strategies
    
    def _calculate_strategy_allocations(self, viable_strategies: List[StrategyRecommendation],
                                      conditions: MarketConditions) -> List[StrategyAllocation]:
        """Calculate final strategy allocations"""
        
        if not viable_strategies:
            return []
        
        # Normalize weights
        total_weight = sum(rec.weight for rec in viable_strategies)
        if total_weight == 0:
            return []
        
        allocations = []
        
        for i, rec in enumerate(viable_strategies[:5]):  # Top 5 strategies max
            normalized_weight = rec.weight / total_weight
            
            # Determine max positions based on weight and strategy type
            if normalized_weight >= 0.4:
                max_positions = 3
            elif normalized_weight >= 0.2:
                max_positions = 2
            else:
                max_positions = 1
            
            allocations.append(StrategyAllocation(
                strategy_name=rec.strategy_name,
                allocation_weight=normalized_weight,
                max_positions=max_positions,
                priority=i + 1
            ))
        
        return allocations
    
    async def generate_adaptive_signals(self, market_data: MarketData) -> List[StrategySignal]:
        """Generate signals using adaptive strategy selection"""
        
        # Select optimal strategies
        allocations = await self.select_strategies(market_data)
        
        if not allocations:
            self.logger.info("No viable strategies for current market conditions")
            return []
        
        all_signals = []
        
        # Generate signals from selected strategies
        for allocation in allocations:
            strategy = self.strategies.get(allocation.strategy_name)
            if not strategy:
                continue
            
            try:
                signals = await strategy.generate_signals(market_data)
                
                # Weight signals by allocation
                for signal in signals:
                    signal.confidence_score *= allocation.allocation_weight
                    signal.metadata = signal.metadata or {}
                    signal.metadata['allocation_weight'] = allocation.allocation_weight
                    signal.metadata['selection_priority'] = allocation.priority
                    
                all_signals.extend(signals)
                
                self.logger.info(
                    f"Generated {len(signals)} signals from {allocation.strategy_name}",
                    allocation_weight=allocation.allocation_weight,
                    priority=allocation.priority
                )
                
            except Exception as e:
                self.logger.error(f"Error generating signals from {allocation.strategy_name}: {e}")
        
        # Sort by weighted confidence
        all_signals.sort(key=lambda x: x.confidence_score, reverse=True)
        
        self.logger.info(
            f"Adaptive signal generation complete",
            total_signals=len(all_signals),
            strategies_used=len(allocations)
        )
        
        return all_signals