from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import statistics

from ..strategies.base_strategy import MarketData
from ..utils.logger import get_logger


class MarketRegime(Enum):
    """Different market regimes for strategy selection"""
    BULL_TRENDING = "bull_trending"        # Strong upward trend, low volatility
    BEAR_TRENDING = "bear_trending"        # Strong downward trend, low volatility  
    BULL_VOLATILE = "bull_volatile"        # Upward trend with high volatility
    BEAR_VOLATILE = "bear_volatile"        # Downward trend with high volatility
    SIDEWAYS_LOW_VOL = "sideways_low_vol"  # Range-bound, low volatility
    SIDEWAYS_HIGH_VOL = "sideways_high_vol" # Range-bound, high volatility
    BREAKOUT_PENDING = "breakout_pending"   # Consolidation before potential breakout
    HIGH_UNCERTAINTY = "high_uncertainty"  # Unclear direction, mixed signals


class VolatilityRegime(Enum):
    """Volatility classification"""
    LOW = "low"           # IV < 20th percentile
    MEDIUM = "medium"     # IV 20th-80th percentile  
    HIGH = "high"         # IV > 80th percentile
    EXTREME = "extreme"   # IV > 95th percentile


class TrendStrength(Enum):
    """Trend strength classification"""
    STRONG = "strong"     # Clear directional move
    MODERATE = "moderate" # Some directional bias
    WEAK = "weak"         # Mixed signals
    NONE = "none"         # No clear direction


@dataclass
class MarketConditions:
    """Complete market analysis summary"""
    regime: MarketRegime
    volatility_regime: VolatilityRegime
    trend_strength: TrendStrength
    trend_direction: str  # "bullish", "bearish", "neutral"
    iv_percentile: float
    momentum_score: float
    mean_reversion_likelihood: float
    breakout_probability: float
    confidence_score: float
    updated_at: datetime
    
    # Raw metrics
    current_iv: float
    historical_iv_avg: float
    price_momentum_1d: float
    price_momentum_5d: float
    volume_profile: str
    support_resistance_strength: float


class MarketRegimeDetector:
    """Advanced market regime detection and analysis"""
    
    def __init__(self):
        self.logger = get_logger("market_regime")
        
        # Historical data storage (in production, this would come from database)
        self.price_history: List[Tuple[datetime, float]] = []
        self.iv_history: List[Tuple[datetime, float]] = []
        self.volume_history: List[Tuple[datetime, int]] = []
        
        # Configuration parameters
        self.lookback_days = 30
        self.trend_threshold = 0.02  # 2% for significant trend
        self.volatility_lookback = 60  # Days for IV percentile calculation
        self.momentum_window = 5  # Days for momentum calculation
        
        # Volatility percentiles (would be calculated from historical data)
        self.iv_percentiles = {
            20: 18.0,  # Low volatility threshold
            50: 25.0,  # Medium volatility
            80: 35.0,  # High volatility threshold
            95: 45.0   # Extreme volatility threshold
        }
        
    def update_market_data(self, market_data: MarketData):
        """Update internal data with new market information"""
        current_time = datetime.now()
        
        # Add to historical data
        self.price_history.append((current_time, market_data.spot_price))
        self.iv_history.append((current_time, market_data.iv))
        self.volume_history.append((current_time, market_data.volume))
        
        # Keep only recent data
        cutoff_time = current_time - timedelta(days=self.lookback_days * 2)
        self.price_history = [(t, p) for t, p in self.price_history if t > cutoff_time]
        self.iv_history = [(t, iv) for t, iv in self.iv_history if t > cutoff_time]
        self.volume_history = [(t, v) for t, v in self.volume_history if t > cutoff_time]
    
    def detect_regime(self, market_data: MarketData) -> MarketConditions:
        """Main function to detect current market regime"""
        self.update_market_data(market_data)
        
        # Analyze different aspects
        volatility_regime = self._analyze_volatility_regime(market_data)
        trend_analysis = self._analyze_trend(market_data)
        momentum_score = self._calculate_momentum_score(market_data)
        mean_reversion_score = self._calculate_mean_reversion_likelihood(market_data)
        breakout_probability = self._calculate_breakout_probability(market_data)
        
        # Determine overall market regime
        regime = self._determine_market_regime(
            volatility_regime, trend_analysis, momentum_score
        )
        
        # Calculate confidence in the analysis
        confidence_score = self._calculate_confidence_score(
            volatility_regime, trend_analysis, momentum_score
        )
        
        # Build market conditions object
        conditions = MarketConditions(
            regime=regime,
            volatility_regime=volatility_regime,
            trend_strength=trend_analysis['strength'],
            trend_direction=trend_analysis['direction'],
            iv_percentile=self._calculate_iv_percentile(market_data.iv),
            momentum_score=momentum_score,
            mean_reversion_likelihood=mean_reversion_score,
            breakout_probability=breakout_probability,
            confidence_score=confidence_score,
            updated_at=datetime.now(),
            current_iv=market_data.iv,
            historical_iv_avg=self._get_historical_iv_average(),
            price_momentum_1d=self._calculate_price_momentum(1),
            price_momentum_5d=self._calculate_price_momentum(5),
            volume_profile=self._analyze_volume_profile(market_data),
            support_resistance_strength=self._calculate_support_resistance_strength(market_data)
        )
        
        self.logger.info(
            "Market regime detected",
            regime=regime.value,
            volatility=volatility_regime.value,
            trend_direction=trend_analysis['direction'],
            confidence=confidence_score
        )
        
        return conditions
    
    def _analyze_volatility_regime(self, market_data: MarketData) -> VolatilityRegime:
        """Classify current volatility regime"""
        iv_percentile = self._calculate_iv_percentile(market_data.iv)
        
        if iv_percentile >= 95:
            return VolatilityRegime.EXTREME
        elif iv_percentile >= 80:
            return VolatilityRegime.HIGH
        elif iv_percentile >= 20:
            return VolatilityRegime.MEDIUM
        else:
            return VolatilityRegime.LOW
    
    def _analyze_trend(self, market_data: MarketData) -> Dict:
        """Analyze trend direction and strength"""
        if len(self.price_history) < 10:
            # Not enough data, return neutral
            return {
                'direction': 'neutral',
                'strength': TrendStrength.NONE,
                'score': 0.0
            }
        
        # Calculate price momentum over different periods
        momentum_1d = self._calculate_price_momentum(1)
        momentum_5d = self._calculate_price_momentum(5) 
        momentum_10d = self._calculate_price_momentum(10)
        
        # Weighted average momentum (recent gets more weight)
        trend_score = (momentum_1d * 0.5 + momentum_5d * 0.3 + momentum_10d * 0.2)
        
        # Determine direction
        if trend_score > self.trend_threshold:
            direction = 'bullish'
        elif trend_score < -self.trend_threshold:
            direction = 'bearish'
        else:
            direction = 'neutral'
        
        # Determine strength
        abs_score = abs(trend_score)
        if abs_score > 0.05:  # > 5%
            strength = TrendStrength.STRONG
        elif abs_score > 0.02:  # > 2%
            strength = TrendStrength.MODERATE
        elif abs_score > 0.01:  # > 1%
            strength = TrendStrength.WEAK
        else:
            strength = TrendStrength.NONE
        
        return {
            'direction': direction,
            'strength': strength,
            'score': trend_score
        }
    
    def _calculate_momentum_score(self, market_data: MarketData) -> float:
        """Calculate overall momentum score (-1 to +1)"""
        if len(self.price_history) < 5:
            return 0.0
        
        # Multiple timeframe momentum
        momentum_1d = self._calculate_price_momentum(1)
        momentum_3d = self._calculate_price_momentum(3)
        momentum_7d = self._calculate_price_momentum(7)
        
        # Volume-weighted momentum (higher volume = more significant)
        current_volume = market_data.volume
        avg_volume = self._get_average_volume(7)
        volume_weight = min(current_volume / avg_volume, 2.0) if avg_volume > 0 else 1.0
        
        # Combine momentums with decreasing weights for longer periods
        raw_momentum = (momentum_1d * 0.5 + momentum_3d * 0.3 + momentum_7d * 0.2)
        
        # Apply volume weighting and normalize
        momentum_score = raw_momentum * volume_weight
        return max(-1.0, min(1.0, momentum_score * 5))  # Scale and cap
    
    def _calculate_mean_reversion_likelihood(self, market_data: MarketData) -> float:
        """Calculate probability of mean reversion (0 to 1)"""
        if len(self.price_history) < 20:
            return 0.5  # Default neutral
        
        current_price = market_data.spot_price
        
        # Calculate distance from moving averages
        ma_20 = self._calculate_moving_average(20)
        ma_10 = self._calculate_moving_average(10)
        ma_5 = self._calculate_moving_average(5)
        
        # Distance from longer-term average indicates mean reversion potential
        distance_from_ma20 = abs(current_price - ma_20) / ma_20 if ma_20 > 0 else 0
        
        # RSI-like calculation for overbought/oversold conditions
        price_changes = []
        for i in range(min(14, len(self.price_history) - 1)):
            curr = self.price_history[-(i+1)][1]
            prev = self.price_history[-(i+2)][1]
            price_changes.append((curr - prev) / prev)
        
        if price_changes:
            avg_gain = statistics.mean([p for p in price_changes if p > 0] or [0])
            avg_loss = abs(statistics.mean([p for p in price_changes if p < 0] or [0]))
            
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi_like = 100 - (100 / (1 + rs))
                
                # Mean reversion more likely at extremes
                if rsi_like > 70 or rsi_like < 30:
                    reversion_score = 0.7 + distance_from_ma20 * 2
                else:
                    reversion_score = 0.3 + distance_from_ma20
            else:
                reversion_score = 0.5
        else:
            reversion_score = 0.5
        
        return max(0.0, min(1.0, reversion_score))
    
    def _calculate_breakout_probability(self, market_data: MarketData) -> float:
        """Calculate probability of breakout from current range (0 to 1)"""
        if len(self.price_history) < 20:
            return 0.3  # Default low probability
        
        # Calculate recent trading range
        recent_prices = [p for _, p in self.price_history[-20:]]
        range_high = max(recent_prices)
        range_low = min(recent_prices)
        range_size = (range_high - range_low) / market_data.spot_price
        
        # Calculate price position within range
        current_price = market_data.spot_price
        position_in_range = (current_price - range_low) / (range_high - range_low) if range_high > range_low else 0.5
        
        # Factors that increase breakout probability
        breakout_factors = []
        
        # 1. Tight range indicates coiling for breakout
        if range_size < 0.03:  # Less than 3% range
            breakout_factors.append(0.3)
        
        # 2. Price near range boundaries
        if position_in_range > 0.9 or position_in_range < 0.1:
            breakout_factors.append(0.4)
        
        # 3. Volume expansion
        current_volume = market_data.volume
        avg_volume = self._get_average_volume(20)
        if current_volume > avg_volume * 1.5:
            breakout_factors.append(0.3)
        
        # 4. Volatility contraction followed by expansion
        current_iv = market_data.iv
        avg_iv = self._get_historical_iv_average()
        if current_iv > avg_iv * 1.2:  # IV expanding
            recent_iv_avg = self._get_recent_iv_average(10)
            if recent_iv_avg < avg_iv * 0.9:  # Was previously contracted
                breakout_factors.append(0.4)
        
        # Combine factors
        base_probability = 0.2
        breakout_probability = base_probability + sum(breakout_factors)
        
        return max(0.0, min(1.0, breakout_probability))
    
    def _determine_market_regime(self, volatility_regime: VolatilityRegime, 
                                trend_analysis: Dict, momentum_score: float) -> MarketRegime:
        """Determine overall market regime based on all factors"""
        direction = trend_analysis['direction']
        strength = trend_analysis['strength']
        
        # High volatility regimes
        if volatility_regime in [VolatilityRegime.HIGH, VolatilityRegime.EXTREME]:
            if direction == 'bullish' and strength in [TrendStrength.STRONG, TrendStrength.MODERATE]:
                return MarketRegime.BULL_VOLATILE
            elif direction == 'bearish' and strength in [TrendStrength.STRONG, TrendStrength.MODERATE]:
                return MarketRegime.BEAR_VOLATILE
            elif direction == 'neutral' or strength == TrendStrength.WEAK:
                return MarketRegime.SIDEWAYS_HIGH_VOL
            else:
                return MarketRegime.HIGH_UNCERTAINTY
        
        # Low volatility regimes
        elif volatility_regime == VolatilityRegime.LOW:
            if direction == 'bullish' and strength == TrendStrength.STRONG:
                return MarketRegime.BULL_TRENDING
            elif direction == 'bearish' and strength == TrendStrength.STRONG:
                return MarketRegime.BEAR_TRENDING
            elif direction == 'neutral' or strength in [TrendStrength.WEAK, TrendStrength.NONE]:
                return MarketRegime.SIDEWAYS_LOW_VOL
            else:
                return MarketRegime.BREAKOUT_PENDING
        
        # Medium volatility regimes  
        else:  # Medium volatility
            if direction == 'bullish' and strength == TrendStrength.STRONG:
                return MarketRegime.BULL_TRENDING
            elif direction == 'bearish' and strength == TrendStrength.STRONG:
                return MarketRegime.BEAR_TRENDING
            elif abs(momentum_score) < 0.3:  # Low momentum
                if volatility_regime == VolatilityRegime.MEDIUM:
                    return MarketRegime.SIDEWAYS_LOW_VOL
                else:
                    return MarketRegime.BREAKOUT_PENDING
            else:
                return MarketRegime.HIGH_UNCERTAINTY
    
    def _calculate_confidence_score(self, volatility_regime: VolatilityRegime,
                                  trend_analysis: Dict, momentum_score: float) -> float:
        """Calculate confidence in the regime detection (0 to 1)"""
        confidence_factors = []
        
        # Data sufficiency
        data_points = len(self.price_history)
        if data_points >= 30:
            confidence_factors.append(0.3)
        elif data_points >= 15:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
        
        # Trend clarity
        trend_score = abs(trend_analysis['score'])
        if trend_score > 0.05:
            confidence_factors.append(0.3)
        elif trend_score > 0.02:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
        
        # Momentum consistency
        if abs(momentum_score) > 0.5:
            confidence_factors.append(0.2)
        elif abs(momentum_score) > 0.3:
            confidence_factors.append(0.15)
        else:
            confidence_factors.append(0.1)
        
        # Volatility regime clarity
        if volatility_regime in [VolatilityRegime.EXTREME, VolatilityRegime.LOW]:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.15)
        
        return min(1.0, sum(confidence_factors))
    
    # Helper methods for calculations
    def _calculate_iv_percentile(self, current_iv: float) -> float:
        """Calculate IV percentile based on historical levels"""
        # Simplified percentile calculation
        if current_iv <= self.iv_percentiles[20]:
            return 10.0
        elif current_iv <= self.iv_percentiles[50]:
            return 40.0
        elif current_iv <= self.iv_percentiles[80]:
            return 70.0
        else:
            return 90.0
    
    def _calculate_price_momentum(self, days: int) -> float:
        """Calculate price momentum over specified days"""
        if len(self.price_history) < days + 1:
            return 0.0
        
        current_price = self.price_history[-1][1]
        past_price = self.price_history[-(days + 1)][1]
        
        return (current_price - past_price) / past_price
    
    def _calculate_moving_average(self, periods: int) -> float:
        """Calculate simple moving average"""
        if len(self.price_history) < periods:
            return 0.0
        
        recent_prices = [p for _, p in self.price_history[-periods:]]
        return statistics.mean(recent_prices)
    
    def _get_historical_iv_average(self) -> float:
        """Get historical IV average"""
        if not self.iv_history:
            return 25.0  # Default
        
        return statistics.mean([iv for _, iv in self.iv_history])
    
    def _get_recent_iv_average(self, days: int) -> float:
        """Get recent IV average"""
        if len(self.iv_history) < days:
            return self._get_historical_iv_average()
        
        recent_iv = [iv for _, iv in self.iv_history[-days:]]
        return statistics.mean(recent_iv)
    
    def _get_average_volume(self, days: int) -> float:
        """Get average volume over specified days"""
        if len(self.volume_history) < days:
            return 0.0
        
        recent_volumes = [v for _, v in self.volume_history[-days:]]
        return statistics.mean(recent_volumes)
    
    def _analyze_volume_profile(self, market_data: MarketData) -> str:
        """Analyze current volume profile"""
        current_volume = market_data.volume
        avg_volume = self._get_average_volume(20)
        
        if avg_volume == 0:
            return "unknown"
        
        ratio = current_volume / avg_volume
        
        if ratio > 2.0:
            return "very_high"
        elif ratio > 1.5:
            return "high"
        elif ratio > 0.8:
            return "normal"
        elif ratio > 0.5:
            return "low"
        else:
            return "very_low"
    
    def _calculate_support_resistance_strength(self, market_data: MarketData) -> float:
        """Calculate strength of nearby support/resistance levels (0 to 1)"""
        if len(self.price_history) < 20:
            return 0.5  # Default neutral
        
        current_price = market_data.spot_price
        recent_prices = [p for _, p in self.price_history[-20:]]
        
        # Find potential support/resistance levels
        price_clusters = {}
        tolerance = current_price * 0.005  # 0.5% tolerance
        
        for price in recent_prices:
            found_cluster = False
            for cluster_price in price_clusters:
                if abs(price - cluster_price) <= tolerance:
                    price_clusters[cluster_price] += 1
                    found_cluster = True
                    break
            
            if not found_cluster:
                price_clusters[price] = 1
        
        # Find strongest cluster near current price
        max_strength = 0
        for cluster_price, count in price_clusters.items():
            if abs(cluster_price - current_price) / current_price <= 0.02:  # Within 2%
                max_strength = max(max_strength, count)
        
        # Normalize strength (max 20 touches = 1.0)
        return min(1.0, max_strength / 20)