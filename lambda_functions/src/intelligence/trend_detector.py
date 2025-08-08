"""
Advanced Trend Detection Algorithms
Provides comprehensive trend analysis using multiple technical indicators and machine learning approaches
"""
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics
import math

from ..strategies.base_strategy import MarketData
from ..utils.logger import get_logger


class TrendDirection(Enum):
    """Primary trend direction"""
    STRONG_UPTREND = "strong_uptrend"
    UPTREND = "uptrend"
    WEAK_UPTREND = "weak_uptrend"
    SIDEWAYS = "sideways"
    WEAK_DOWNTREND = "weak_downtrend"
    DOWNTREND = "downtrend"
    STRONG_DOWNTREND = "strong_downtrend"


class TrendStrength(Enum):
    """Trend strength classification"""
    VERY_WEAK = "very_weak"      # < 20th percentile
    WEAK = "weak"                # 20-40th percentile
    MODERATE = "moderate"        # 40-60th percentile
    STRONG = "strong"            # 60-80th percentile
    VERY_STRONG = "very_strong"  # > 80th percentile


class TrendDuration(Enum):
    """Trend duration classification"""
    MICRO = "micro"          # < 5 periods
    SHORT = "short"          # 5-20 periods
    MEDIUM = "medium"        # 20-50 periods
    LONG = "long"           # 50-200 periods
    SECULAR = "secular"     # > 200 periods


class TrendPhase(Enum):
    """Current phase within trend"""
    EMERGING = "emerging"        # Trend just starting
    ACCELERATING = "accelerating" # Trend gaining momentum
    MATURE = "mature"           # Trend well established
    EXHAUSTING = "exhausting"   # Trend showing signs of fatigue
    REVERSING = "reversing"     # Trend changing direction


@dataclass
class TrendMetrics:
    """Comprehensive trend analysis results"""
    symbol: str
    timestamp: datetime
    
    # Primary trend characteristics
    trend_direction: TrendDirection = TrendDirection.SIDEWAYS
    trend_strength: TrendStrength = TrendStrength.MODERATE
    trend_duration: TrendDuration = TrendDuration.SHORT
    trend_phase: TrendPhase = TrendPhase.MATURE
    
    # Trend measurements
    trend_angle: float = 0.0              # Degrees from horizontal
    trend_slope: float = 0.0              # Price change per period
    trend_r_squared: float = 0.0          # Linearity measure (0-1)
    trend_momentum: float = 0.0           # Rate of change
    
    # Multi-timeframe analysis
    short_term_trend: TrendDirection = TrendDirection.SIDEWAYS     # 5-20 periods
    medium_term_trend: TrendDirection = TrendDirection.SIDEWAYS    # 20-50 periods
    long_term_trend: TrendDirection = TrendDirection.SIDEWAYS      # 50-200 periods
    
    # Trend confirmation indicators
    adx_value: float = 0.0                # Average Directional Index
    macd_signal: float = 0.0              # MACD histogram
    rsi_trend: float = 50.0               # RSI trend bias
    volume_confirmation: float = 0.0       # Volume trend confirmation
    
    # Support/Resistance levels
    key_support_levels: List[float] = None
    key_resistance_levels: List[float] = None
    current_level_significance: float = 0.0
    
    # Trend reversal signals
    reversal_probability: float = 0.0      # 0-1 probability of reversal
    reversal_signals_count: int = 0
    divergence_signals: List[str] = None
    
    # Price action patterns
    higher_highs_count: int = 0
    higher_lows_count: int = 0
    lower_highs_count: int = 0
    lower_lows_count: int = 0
    
    # Trend reliability metrics
    trend_consistency: float = 0.0         # How consistent the trend is
    trend_volatility: float = 0.0          # Volatility within trend
    trend_confidence: float = 0.0          # Overall confidence in trend
    
    def __post_init__(self):
        if self.key_support_levels is None:
            self.key_support_levels = []
        if self.key_resistance_levels is None:
            self.key_resistance_levels = []
        if self.divergence_signals is None:
            self.divergence_signals = []


class TrendDetector:
    """Advanced trend detection and analysis engine"""
    
    def __init__(self):
        self.logger = get_logger("trend_detector")
        
        # Historical data storage
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.volume_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.indicator_cache: Dict[str, Dict[str, List[float]]] = {}
        
        # Trend detection parameters
        self.config = {
            'timeframes': {
                'short': 20,     # periods
                'medium': 50,    # periods
                'long': 200      # periods
            },
            'trend_thresholds': {
                'strong_trend_min': 25,      # degrees
                'moderate_trend_min': 10,    # degrees
                'weak_trend_min': 3,         # degrees
            },
            'adx_parameters': {
                'period': 14,
                'trend_threshold': 25,
                'strong_trend': 40
            },
            'macd_parameters': {
                'fast': 12,
                'slow': 26,
                'signal': 9
            },
            'rsi_parameters': {
                'period': 14,
                'overbought': 70,
                'oversold': 30
            },
            'support_resistance': {
                'min_touches': 2,
                'proximity_threshold': 0.02  # 2%
            }
        }
        
        self.logger.info("Trend detector initialized")
    
    def detect_trend(self, market_data: MarketData, 
                    price_history: Optional[List[float]] = None,
                    volume_history: Optional[List[float]] = None) -> TrendMetrics:
        """Comprehensive trend analysis for given market data"""
        
        try:
            symbol = market_data.symbol
            current_time = market_data.last_updated
            
            # Update internal data storage
            self._update_data_history(symbol, market_data, current_time)
            
            # Use provided history or internal history
            if price_history:
                prices = price_history
            else:
                prices = self._get_price_history(symbol)
            
            if volume_history:
                volumes = volume_history
            else:
                volumes = self._get_volume_history(symbol)
            
            if len(prices) < 20:
                self.logger.warning(f"Insufficient price history for trend analysis: {symbol}")
                return self._create_default_metrics(symbol, current_time)
            
            # Calculate primary trend characteristics
            trend_direction, trend_angle, trend_slope = self._analyze_primary_trend(prices)
            trend_strength = self._calculate_trend_strength(prices, trend_slope)
            trend_duration = self._estimate_trend_duration(prices)
            trend_phase = self._identify_trend_phase(prices)
            
            # Multi-timeframe analysis
            short_trend = self._analyze_timeframe_trend(prices, self.config['timeframes']['short'])
            medium_trend = self._analyze_timeframe_trend(prices, self.config['timeframes']['medium'])
            long_trend = self._analyze_timeframe_trend(prices, self.config['timeframes']['long'])
            
            # Calculate technical indicators
            adx_value = self._calculate_adx(prices)
            macd_signal = self._calculate_macd_signal(prices)
            rsi_trend = self._calculate_rsi_trend(prices)
            volume_confirmation = self._analyze_volume_confirmation(prices, volumes)
            
            # Support and resistance analysis
            support_levels = self._find_support_levels(prices)
            resistance_levels = self._find_resistance_levels(prices)
            current_level_significance = self._assess_current_level_significance(
                market_data.spot_price, support_levels, resistance_levels
            )
            
            # Trend reversal analysis
            reversal_probability = self._calculate_reversal_probability(prices, volumes)
            reversal_signals = self._count_reversal_signals(prices, volumes)
            divergence_signals = self._detect_divergence_signals(prices, volumes)
            
            # Price action pattern analysis
            hh_count, hl_count, lh_count, ll_count = self._analyze_price_action_patterns(prices)
            
            # Trend reliability metrics
            trend_consistency = self._calculate_trend_consistency(prices)
            trend_volatility = self._calculate_trend_volatility(prices)
            trend_r_squared = self._calculate_trend_linearity(prices)
            trend_momentum = self._calculate_trend_momentum(prices)
            
            # Calculate overall confidence
            trend_confidence = self._calculate_trend_confidence(
                trend_strength, trend_consistency, trend_r_squared, adx_value
            )
            
            metrics = TrendMetrics(
                symbol=symbol,
                timestamp=current_time,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                trend_duration=trend_duration,
                trend_phase=trend_phase,
                trend_angle=trend_angle,
                trend_slope=trend_slope,
                trend_r_squared=trend_r_squared,
                trend_momentum=trend_momentum,
                short_term_trend=short_trend,
                medium_term_trend=medium_trend,
                long_term_trend=long_trend,
                adx_value=adx_value,
                macd_signal=macd_signal,
                rsi_trend=rsi_trend,
                volume_confirmation=volume_confirmation,
                key_support_levels=support_levels,
                key_resistance_levels=resistance_levels,
                current_level_significance=current_level_significance,
                reversal_probability=reversal_probability,
                reversal_signals_count=reversal_signals,
                divergence_signals=divergence_signals,
                higher_highs_count=hh_count,
                higher_lows_count=hl_count,
                lower_highs_count=lh_count,
                lower_lows_count=ll_count,
                trend_consistency=trend_consistency,
                trend_volatility=trend_volatility,
                trend_confidence=trend_confidence
            )
            
            self.logger.info(
                "Trend analysis completed",
                symbol=symbol,
                trend_direction=trend_direction.value,
                trend_strength=trend_strength.value,
                trend_confidence=trend_confidence,
                adx_value=adx_value
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Trend detection failed for {market_data.symbol}: {e}")
            return self._create_default_metrics(market_data.symbol, market_data.last_updated)
    
    def _analyze_primary_trend(self, prices: List[float]) -> Tuple[TrendDirection, float, float]:
        """Analyze primary trend using linear regression"""
        if len(prices) < 10:
            return TrendDirection.SIDEWAYS, 0.0, 0.0
        
        # Use recent 50 periods for primary trend
        recent_prices = prices[-min(50, len(prices)):]
        n = len(recent_prices)
        x = list(range(n))
        
        # Linear regression
        sum_x = sum(x)
        sum_y = sum(recent_prices)
        sum_xy = sum(x[i] * recent_prices[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 == sum_x ** 2:  # Avoid division by zero
            return TrendDirection.SIDEWAYS, 0.0, 0.0
        
        # Calculate slope and angle
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # Convert slope to angle (degrees)
        avg_price = statistics.mean(recent_prices)
        relative_slope = slope / avg_price if avg_price > 0 else 0
        angle = math.degrees(math.atan(relative_slope * 100))  # Scale for visibility
        
        # Classify trend direction based on angle
        abs_angle = abs(angle)
        if abs_angle < self.config['trend_thresholds']['weak_trend_min']:
            direction = TrendDirection.SIDEWAYS
        elif angle > 0:  # Uptrend
            if abs_angle >= self.config['trend_thresholds']['strong_trend_min']:
                direction = TrendDirection.STRONG_UPTREND
            elif abs_angle >= self.config['trend_thresholds']['moderate_trend_min']:
                direction = TrendDirection.UPTREND
            else:
                direction = TrendDirection.WEAK_UPTREND
        else:  # Downtrend
            if abs_angle >= self.config['trend_thresholds']['strong_trend_min']:
                direction = TrendDirection.STRONG_DOWNTREND
            elif abs_angle >= self.config['trend_thresholds']['moderate_trend_min']:
                direction = TrendDirection.DOWNTREND
            else:
                direction = TrendDirection.WEAK_DOWNTREND
        
        return direction, angle, slope
    
    def _calculate_trend_strength(self, prices: List[float], slope: float) -> TrendStrength:
        """Calculate trend strength using multiple factors"""
        if len(prices) < 10:
            return TrendStrength.WEAK
        
        # Factor 1: Slope magnitude
        avg_price = statistics.mean(prices[-20:])
        relative_slope = abs(slope / avg_price) if avg_price > 0 else 0
        slope_score = min(1.0, relative_slope * 1000)  # Scale appropriately
        
        # Factor 2: Price momentum
        momentum_score = self._calculate_momentum_score(prices)
        
        # Factor 3: Trend consistency (R-squared)
        r_squared = self._calculate_trend_linearity(prices)
        
        # Combine factors
        strength_score = (slope_score * 0.4 + momentum_score * 0.3 + r_squared * 0.3)
        
        # Classify strength
        if strength_score >= 0.8:
            return TrendStrength.VERY_STRONG
        elif strength_score >= 0.6:
            return TrendStrength.STRONG
        elif strength_score >= 0.4:
            return TrendStrength.MODERATE
        elif strength_score >= 0.2:
            return TrendStrength.WEAK
        else:
            return TrendStrength.VERY_WEAK
    
    def _estimate_trend_duration(self, prices: List[float]) -> TrendDuration:
        """Estimate how long the current trend has been in place"""
        if len(prices) < 10:
            return TrendDuration.MICRO
        
        # Simple heuristic: count periods since last trend change
        # In a more sophisticated implementation, this would track actual trend changes
        trend_periods = min(len(prices), 50)  # Simplified approach
        
        if trend_periods < 5:
            return TrendDuration.MICRO
        elif trend_periods < 20:
            return TrendDuration.SHORT
        elif trend_periods < 50:
            return TrendDuration.MEDIUM
        elif trend_periods < 200:
            return TrendDuration.LONG
        else:
            return TrendDuration.SECULAR
    
    def _identify_trend_phase(self, prices: List[float]) -> TrendPhase:
        """Identify current phase within the trend"""
        if len(prices) < 20:
            return TrendPhase.EMERGING
        
        # Calculate momentum over different periods
        recent_momentum = self._calculate_period_momentum(prices[-10:])
        medium_momentum = self._calculate_period_momentum(prices[-20:])
        
        # Analyze momentum patterns
        if abs(recent_momentum) > abs(medium_momentum) * 1.5:
            return TrendPhase.ACCELERATING
        elif abs(recent_momentum) < abs(medium_momentum) * 0.5:
            return TrendPhase.EXHAUSTING
        elif self._detect_trend_reversal_signals(prices):
            return TrendPhase.REVERSING
        elif len(prices) >= 50:
            return TrendPhase.MATURE
        else:
            return TrendPhase.EMERGING
    
    def _analyze_timeframe_trend(self, prices: List[float], periods: int) -> TrendDirection:
        """Analyze trend for specific timeframe"""
        if len(prices) < periods:
            return TrendDirection.SIDEWAYS
        
        timeframe_prices = prices[-periods:]
        direction, _, _ = self._analyze_primary_trend(timeframe_prices)
        return direction
    
    def _calculate_adx(self, prices: List[float]) -> float:
        """Calculate Average Directional Index (simplified)"""
        if len(prices) < self.config['adx_parameters']['period'] + 1:
            return 25.0  # Neutral value
        
        period = self.config['adx_parameters']['period']
        
        # Calculate True Range and Directional Movement
        high_prices = prices  # Simplified: using close as high
        low_prices = prices   # Simplified: using close as low
        
        # Simplified ADX calculation
        movements = []
        for i in range(1, len(prices)):
            movement = abs(prices[i] - prices[i-1])
            movements.append(movement)
        
        if len(movements) < period:
            return 25.0
        
        # Average movement over period
        avg_movement = statistics.mean(movements[-period:])
        
        # Convert to ADX-like value (0-100 scale)
        adx_value = min(100, avg_movement / statistics.mean(prices[-period:]) * 1000)
        
        return adx_value
    
    def _calculate_macd_signal(self, prices: List[float]) -> float:
        """Calculate MACD signal (simplified)"""
        fast_period = self.config['macd_parameters']['fast']
        slow_period = self.config['macd_parameters']['slow']
        signal_period = self.config['macd_parameters']['signal']
        
        if len(prices) < slow_period:
            return 0.0
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(prices, fast_period)
        slow_ema = self._calculate_ema(prices, slow_period)
        
        if not fast_ema or not slow_ema:
            return 0.0
        
        # MACD line
        macd_line = fast_ema[-1] - slow_ema[-1]
        
        # Simplified signal - return MACD line value
        return macd_line / prices[-1] * 100 if prices[-1] > 0 else 0.0
    
    def _calculate_rsi_trend(self, prices: List[float]) -> float:
        """Calculate RSI and determine trend bias"""
        period = self.config['rsi_parameters']['period']
        
        if len(prices) < period + 1:
            return 50.0
        
        # Calculate price changes
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        if len(changes) < period:
            return 50.0
        
        # Calculate gains and losses
        gains = [max(0, change) for change in changes[-period:]]
        losses = [max(0, -change) for change in changes[-period:]]
        
        avg_gain = statistics.mean(gains) if gains else 0
        avg_loss = statistics.mean(losses) if losses else 0
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _analyze_volume_confirmation(self, prices: List[float], volumes: List[float]) -> float:
        """Analyze volume confirmation of price trend"""
        if not volumes or len(volumes) != len(prices) or len(prices) < 10:
            return 0.5  # Neutral
        
        recent_periods = min(20, len(prices))
        recent_prices = prices[-recent_periods:]
        recent_volumes = volumes[-recent_periods:]
        
        # Calculate price and volume trends
        price_trend = recent_prices[-1] - recent_prices[0]
        volume_trend = statistics.mean(recent_volumes[-5:]) - statistics.mean(recent_volumes[:5])
        
        # Volume confirmation: volume should increase with price trend
        if price_trend > 0 and volume_trend > 0:
            return 0.8  # Strong uptrend confirmation
        elif price_trend < 0 and volume_trend > 0:
            return 0.2  # Strong downtrend confirmation
        else:
            return 0.5  # Neutral/weak confirmation
    
    def _find_support_levels(self, prices: List[float]) -> List[float]:
        """Find key support levels"""
        if len(prices) < 20:
            return []
        
        # Find local minima
        support_levels = []
        for i in range(2, len(prices) - 2):
            if (prices[i] < prices[i-1] and prices[i] < prices[i-2] and 
                prices[i] < prices[i+1] and prices[i] < prices[i+2]):
                support_levels.append(prices[i])
        
        # Group nearby levels and return strongest ones
        return self._consolidate_levels(support_levels)[:5]  # Top 5 support levels
    
    def _find_resistance_levels(self, prices: List[float]) -> List[float]:
        """Find key resistance levels"""
        if len(prices) < 20:
            return []
        
        # Find local maxima
        resistance_levels = []
        for i in range(2, len(prices) - 2):
            if (prices[i] > prices[i-1] and prices[i] > prices[i-2] and 
                prices[i] > prices[i+1] and prices[i] > prices[i+2]):
                resistance_levels.append(prices[i])
        
        # Group nearby levels and return strongest ones
        return self._consolidate_levels(resistance_levels)[:5]  # Top 5 resistance levels
    
    def _consolidate_levels(self, levels: List[float]) -> List[float]:
        """Consolidate nearby price levels"""
        if not levels:
            return []
        
        consolidated = []
        sorted_levels = sorted(levels)
        
        current_group = [sorted_levels[0]]
        threshold = statistics.mean(sorted_levels) * self.config['support_resistance']['proximity_threshold']
        
        for level in sorted_levels[1:]:
            if level - current_group[-1] <= threshold:
                current_group.append(level)
            else:
                # Take average of current group
                consolidated.append(statistics.mean(current_group))
                current_group = [level]
        
        # Add final group
        if current_group:
            consolidated.append(statistics.mean(current_group))
        
        return consolidated
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [statistics.mean(prices[:period])]  # Start with SMA
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def _calculate_momentum_score(self, prices: List[float]) -> float:
        """Calculate momentum score (0-1)"""
        if len(prices) < 5:
            return 0.5
        
        # Rate of change over different periods
        roc_5 = (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 and prices[-5] > 0 else 0
        roc_10 = (prices[-1] - prices[-10]) / prices[-10] if len(prices) >= 10 and prices[-10] > 0 else 0
        
        momentum = (abs(roc_5) + abs(roc_10)) / 2
        return min(1.0, momentum * 50)  # Scale to 0-1
    
    def _calculate_trend_linearity(self, prices: List[float]) -> float:
        """Calculate R-squared for trend linearity"""
        if len(prices) < 10:
            return 0.0
        
        recent_prices = prices[-min(50, len(prices)):]
        n = len(recent_prices)
        x = list(range(n))
        
        # Linear regression
        sum_x = sum(x)
        sum_y = sum(recent_prices)
        sum_xy = sum(x[i] * recent_prices[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y ** 2 for y in recent_prices)
        
        if n * sum_x2 == sum_x ** 2:
            return 0.0
        
        # Calculate correlation coefficient
        numerator = n * sum_xy - sum_x * sum_y
        denominator_x = n * sum_x2 - sum_x ** 2
        denominator_y = n * sum_y2 - sum_y ** 2
        
        if denominator_x <= 0 or denominator_y <= 0:
            return 0.0
        
        correlation = numerator / math.sqrt(denominator_x * denominator_y)
        r_squared = correlation ** 2
        
        return r_squared
    
    def _calculate_trend_momentum(self, prices: List[float]) -> float:
        """Calculate overall trend momentum"""
        if len(prices) < 10:
            return 0.0
        
        # Compare recent momentum with historical
        recent_momentum = self._calculate_period_momentum(prices[-10:])
        historical_momentum = self._calculate_period_momentum(prices[-30:])
        
        if historical_momentum == 0:
            return recent_momentum
        
        return recent_momentum / historical_momentum
    
    def _calculate_period_momentum(self, prices: List[float]) -> float:
        """Calculate momentum for a specific period"""
        if len(prices) < 2:
            return 0.0
        
        return (prices[-1] - prices[0]) / prices[0] if prices[0] > 0 else 0.0
    
    # Helper methods (simplified implementations)
    def _assess_current_level_significance(self, current_price: float, 
                                         support_levels: List[float], 
                                         resistance_levels: List[float]) -> float:
        """Assess significance of current price level"""
        # Simplified implementation
        return 0.5  # Neutral
    
    def _calculate_reversal_probability(self, prices: List[float], volumes: List[float]) -> float:
        """Calculate probability of trend reversal"""
        # Simplified implementation
        return 0.3  # Low reversal probability
    
    def _count_reversal_signals(self, prices: List[float], volumes: List[float]) -> int:
        """Count active reversal signals"""
        # Simplified implementation
        return 0
    
    def _detect_divergence_signals(self, prices: List[float], volumes: List[float]) -> List[str]:
        """Detect momentum divergence signals"""
        # Simplified implementation
        return []
    
    def _analyze_price_action_patterns(self, prices: List[float]) -> Tuple[int, int, int, int]:
        """Analyze higher highs, higher lows, lower highs, lower lows"""
        if len(prices) < 4:
            return 0, 0, 0, 0
        
        hh_count = hl_count = lh_count = ll_count = 0
        
        # Simple pattern detection over recent periods
        for i in range(2, min(len(prices), 20)):
            if prices[-i] > prices[-(i+1)]:  # Higher value
                if i % 2 == 0:  # Even positions (highs)
                    hh_count += 1
                else:  # Odd positions (lows)
                    hl_count += 1
            else:  # Lower value
                if i % 2 == 0:  # Even positions (highs)
                    lh_count += 1
                else:  # Odd positions (lows)
                    ll_count += 1
        
        return hh_count, hl_count, lh_count, ll_count
    
    def _calculate_trend_consistency(self, prices: List[float]) -> float:
        """Calculate how consistent the trend is"""
        if len(prices) < 10:
            return 0.5
        
        # Calculate rolling correlations
        consistency_scores = []
        window_size = min(20, len(prices) // 2)
        
        for i in range(window_size, len(prices) - window_size):
            window_prices = prices[i-window_size:i+window_size]
            r_squared = self._calculate_trend_linearity(window_prices)
            consistency_scores.append(r_squared)
        
        return statistics.mean(consistency_scores) if consistency_scores else 0.5
    
    def _calculate_trend_volatility(self, prices: List[float]) -> float:
        """Calculate volatility within trend"""
        if len(prices) < 10:
            return 0.0
        
        # Detrend the prices first
        detrended = self._detrend_prices(prices)
        
        # Calculate volatility of detrended series
        if len(detrended) > 1:
            return statistics.stdev(detrended) / statistics.mean(prices) * 100
        return 0.0
    
    def _detrend_prices(self, prices: List[float]) -> List[float]:
        """Remove trend from price series"""
        if len(prices) < 3:
            return prices
        
        # Simple linear detrending
        n = len(prices)
        x = list(range(n))
        
        # Linear regression
        sum_x = sum(x)
        sum_y = sum(prices)
        sum_xy = sum(x[i] * prices[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 == sum_x ** 2:
            return prices
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # Remove trend
        trend_line = [intercept + slope * i for i in x]
        detrended = [prices[i] - trend_line[i] for i in range(n)]
        
        return detrended
    
    def _calculate_trend_confidence(self, strength: TrendStrength, consistency: float, 
                                  r_squared: float, adx_value: float) -> float:
        """Calculate overall trend confidence"""
        # Strength score
        strength_scores = {
            TrendStrength.VERY_STRONG: 1.0,
            TrendStrength.STRONG: 0.8,
            TrendStrength.MODERATE: 0.6,
            TrendStrength.WEAK: 0.4,
            TrendStrength.VERY_WEAK: 0.2
        }
        strength_score = strength_scores[strength]
        
        # ADX score (normalized to 0-1)
        adx_score = min(1.0, adx_value / 100)
        
        # Combine all factors
        confidence = (strength_score * 0.3 + consistency * 0.25 + 
                     r_squared * 0.25 + adx_score * 0.2)
        
        return confidence
    
    def _detect_trend_reversal_signals(self, prices: List[float]) -> bool:
        """Detect if trend reversal signals are present"""
        # Simplified implementation
        return False
    
    def _update_data_history(self, symbol: str, market_data: MarketData, timestamp: datetime):
        """Update internal data storage"""
        # Update price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append((timestamp, market_data.spot_price))
        
        # Update volume history
        if symbol not in self.volume_history:
            self.volume_history[symbol] = []
        
        self.volume_history[symbol].append((timestamp, market_data.volume))
        
        # Keep only recent history (1 year max)
        cutoff_date = timestamp - timedelta(days=365)
        self.price_history[symbol] = [
            (date, price) for date, price in self.price_history[symbol]
            if date >= cutoff_date
        ]
        self.volume_history[symbol] = [
            (date, volume) for date, volume in self.volume_history[symbol]
            if date >= cutoff_date
        ]
    
    def _get_price_history(self, symbol: str) -> List[float]:
        """Get price history for symbol"""
        if symbol not in self.price_history:
            return []
        return [price for _, price in self.price_history[symbol]]
    
    def _get_volume_history(self, symbol: str) -> List[float]:
        """Get volume history for symbol"""
        if symbol not in self.volume_history:
            return []
        return [volume for _, volume in self.volume_history[symbol]]
    
    def _create_default_metrics(self, symbol: str, timestamp: datetime) -> TrendMetrics:
        """Create default trend metrics when analysis fails"""
        return TrendMetrics(
            symbol=symbol,
            timestamp=timestamp,
            trend_direction=TrendDirection.SIDEWAYS,
            trend_strength=TrendStrength.MODERATE,
            trend_duration=TrendDuration.SHORT,
            trend_phase=TrendPhase.MATURE,
            trend_confidence=0.5
        )
    
    def get_trend_summary(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive trend summary for symbol"""
        if symbol not in self.price_history or not self.price_history[symbol]:
            return {"error": "No price history available"}
        
        prices = [price for _, price in self.price_history[symbol]]
        if not prices:
            return {"error": "No price data"}
        
        direction, angle, slope = self._analyze_primary_trend(prices)
        
        return {
            "symbol": symbol,
            "trend_direction": direction.value,
            "trend_angle": angle,
            "current_price": prices[-1] if prices else 0,
            "price_change": prices[-1] - prices[0] if len(prices) > 1 else 0,
            "data_points": len(prices)
        }