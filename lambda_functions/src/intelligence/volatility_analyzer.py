"""
Advanced Volatility Analysis Module
Provides comprehensive volatility metrics, forecasting, and regime classification
"""
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics
import math

from ..strategies.base_strategy import MarketData
from ..utils.logger import get_logger


class VolatilityRegime(Enum):
    """Enhanced volatility regime classification"""
    ULTRA_LOW = "ultra_low"      # < 5th percentile
    LOW = "low"                  # 5th-25th percentile  
    NORMAL = "normal"            # 25th-75th percentile
    ELEVATED = "elevated"        # 75th-90th percentile
    HIGH = "high"               # 90th-95th percentile
    EXTREME = "extreme"         # > 95th percentile


class VolatilityTrend(Enum):
    """Volatility trend direction"""
    DECLINING = "declining"
    STABLE = "stable"
    RISING = "rising"
    SPIKING = "spiking"


@dataclass
class VolatilityMetrics:
    """Comprehensive volatility analysis results"""
    symbol: str
    timestamp: datetime
    
    # Current volatility measures
    realized_vol_daily: float = 0.0
    realized_vol_weekly: float = 0.0
    realized_vol_monthly: float = 0.0
    implied_vol_current: float = 0.0
    
    # Historical context
    vol_percentile_30d: float = 0.0
    vol_percentile_90d: float = 0.0
    vol_percentile_1y: float = 0.0
    
    # Volatility regime
    current_regime: VolatilityRegime = VolatilityRegime.NORMAL
    regime_confidence: float = 0.0
    regime_stability: float = 0.0
    
    # Volatility forecasting
    predicted_vol_1d: float = 0.0
    predicted_vol_5d: float = 0.0
    predicted_vol_30d: float = 0.0
    vol_forecast_confidence: float = 0.0
    
    # Volatility structure
    vol_term_structure: Dict[str, float] = None
    vol_skew_measure: float = 0.0
    vol_smile_curvature: float = 0.0
    
    # Volatility dynamics
    vol_trend: VolatilityTrend = VolatilityTrend.STABLE
    vol_acceleration: float = 0.0
    vol_mean_reversion_speed: float = 0.0
    
    # Risk metrics
    vol_risk_premium: float = 0.0
    vol_uncertainty_index: float = 0.0
    tail_risk_indicator: float = 0.0
    
    def __post_init__(self):
        if self.vol_term_structure is None:
            self.vol_term_structure = {}


class VolatilityAnalyzer:
    """Advanced volatility analysis and forecasting engine"""
    
    def __init__(self):
        self.logger = get_logger("volatility_analyzer")
        
        # Historical volatility storage
        self.vol_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        
        # Volatility calibration parameters
        self.config = {
            'lookback_periods': {
                'short': 10,    # days
                'medium': 30,   # days
                'long': 90,     # days
                'yearly': 252   # trading days
            },
            'percentile_windows': [30, 90, 252],
            'garch_parameters': {
                'alpha': 0.1,   # ARCH coefficient
                'beta': 0.8,    # GARCH coefficient
                'omega': 0.01   # Long-term variance
            },
            'regime_thresholds': {
                'ultra_low': 0.05,
                'low': 0.25,
                'elevated': 0.75,
                'high': 0.90,
                'extreme': 0.95
            }
        }
        
        # Volatility models
        self.volatility_models = {
            'ewma': self._calculate_ewma_volatility,
            'garch': self._calculate_garch_volatility,
            'realized': self._calculate_realized_volatility
        }
        
        self.logger.info("Volatility analyzer initialized")
    
    def analyze_volatility(self, market_data: MarketData, 
                         price_history: Optional[List[float]] = None) -> VolatilityMetrics:
        """Comprehensive volatility analysis for given market data"""
        
        try:
            symbol = market_data.symbol
            current_time = market_data.last_updated
            
            # Update internal data storage
            self._update_price_history(symbol, market_data.spot_price, current_time)
            
            # Use provided history or internal history
            if price_history:
                prices = price_history
            else:
                prices = self._get_price_history(symbol)
            
            if len(prices) < 10:
                self.logger.warning(f"Insufficient price history for {symbol}")
                return self._create_default_metrics(symbol, current_time)
            
            # Calculate realized volatility at different horizons
            realized_vol_daily = self._calculate_realized_volatility(prices[-10:])
            realized_vol_weekly = self._calculate_realized_volatility(prices[-30:])
            realized_vol_monthly = self._calculate_realized_volatility(prices[-90:] if len(prices) >= 90 else prices)
            
            # Calculate historical percentiles
            vol_percentile_30d = self._calculate_vol_percentile(symbol, realized_vol_daily, 30)
            vol_percentile_90d = self._calculate_vol_percentile(symbol, realized_vol_daily, 90)
            vol_percentile_1y = self._calculate_vol_percentile(symbol, realized_vol_daily, 252)
            
            # Determine volatility regime
            current_regime, regime_confidence = self._classify_vol_regime(vol_percentile_90d)
            regime_stability = self._calculate_regime_stability(symbol)
            
            # Volatility forecasting
            predicted_vols = self._forecast_volatility(prices)
            
            # Calculate volatility dynamics
            vol_trend = self._analyze_vol_trend(symbol)
            vol_acceleration = self._calculate_vol_acceleration(symbol)
            mean_reversion_speed = self._calculate_mean_reversion_speed(symbol)
            
            # Risk metrics
            vol_risk_premium = self._calculate_vol_risk_premium(market_data.iv, realized_vol_monthly)
            uncertainty_index = self._calculate_uncertainty_index(symbol)
            tail_risk = self._calculate_tail_risk_indicator(prices)
            
            # Term structure (if options data available)
            term_structure = self._analyze_vol_term_structure(market_data)
            
            metrics = VolatilityMetrics(
                symbol=symbol,
                timestamp=current_time,
                realized_vol_daily=realized_vol_daily,
                realized_vol_weekly=realized_vol_weekly,
                realized_vol_monthly=realized_vol_monthly,
                implied_vol_current=market_data.iv,
                vol_percentile_30d=vol_percentile_30d,
                vol_percentile_90d=vol_percentile_90d,
                vol_percentile_1y=vol_percentile_1y,
                current_regime=current_regime,
                regime_confidence=regime_confidence,
                regime_stability=regime_stability,
                predicted_vol_1d=predicted_vols.get('1d', realized_vol_daily),
                predicted_vol_5d=predicted_vols.get('5d', realized_vol_weekly),
                predicted_vol_30d=predicted_vols.get('30d', realized_vol_monthly),
                vol_forecast_confidence=predicted_vols.get('confidence', 0.5),
                vol_term_structure=term_structure,
                vol_skew_measure=self._calculate_vol_skew(market_data),
                vol_trend=vol_trend,
                vol_acceleration=vol_acceleration,
                vol_mean_reversion_speed=mean_reversion_speed,
                vol_risk_premium=vol_risk_premium,
                vol_uncertainty_index=uncertainty_index,
                tail_risk_indicator=tail_risk
            )
            
            self.logger.info(
                "Volatility analysis completed",
                symbol=symbol,
                regime=current_regime.value,
                realized_vol=realized_vol_daily,
                implied_vol=market_data.iv,
                vol_percentile=vol_percentile_90d
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Volatility analysis failed for {market_data.symbol}: {e}")
            return self._create_default_metrics(market_data.symbol, market_data.last_updated)
    
    def _calculate_realized_volatility(self, prices: List[float], annualized: bool = True) -> float:
        """Calculate realized volatility from price series"""
        if len(prices) < 2:
            return 0.0
        
        # Calculate log returns
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                returns.append(math.log(prices[i] / prices[i-1]))
        
        if not returns:
            return 0.0
        
        # Calculate standard deviation
        vol = statistics.stdev(returns) if len(returns) > 1 else 0.0
        
        # Annualize if requested (assuming daily returns)
        if annualized:
            vol *= math.sqrt(252)  # 252 trading days
        
        return vol * 100  # Convert to percentage
    
    def _calculate_ewma_volatility(self, prices: List[float], lambda_param: float = 0.94) -> float:
        """Calculate Exponentially Weighted Moving Average volatility"""
        if len(prices) < 2:
            return 0.0
        
        # Calculate returns
        returns = [math.log(prices[i] / prices[i-1]) for i in range(1, len(prices)) if prices[i-1] > 0]
        
        if not returns:
            return 0.0
        
        # Initialize with first squared return
        ewma_var = returns[0] ** 2
        
        # Update EWMA variance
        for r in returns[1:]:
            ewma_var = lambda_param * ewma_var + (1 - lambda_param) * (r ** 2)
        
        return math.sqrt(ewma_var * 252) * 100  # Annualized percentage
    
    def _calculate_garch_volatility(self, prices: List[float]) -> float:
        """Simplified GARCH(1,1) volatility estimation"""
        if len(prices) < 10:
            return self._calculate_realized_volatility(prices)
        
        # Calculate returns
        returns = [math.log(prices[i] / prices[i-1]) for i in range(1, len(prices)) if prices[i-1] > 0]
        
        if len(returns) < 5:
            return 0.0
        
        # GARCH parameters from config
        omega = self.config['garch_parameters']['omega']
        alpha = self.config['garch_parameters']['alpha']
        beta = self.config['garch_parameters']['beta']
        
        # Initialize variance
        long_term_var = statistics.variance(returns)
        variance = long_term_var
        
        # Update GARCH variance for recent periods
        for r in returns[-min(30, len(returns)):]:
            variance = omega + alpha * (r ** 2) + beta * variance
        
        return math.sqrt(variance * 252) * 100  # Annualized percentage
    
    def _calculate_vol_percentile(self, symbol: str, current_vol: float, window_days: int) -> float:
        """Calculate percentile rank of current volatility vs historical"""
        if symbol not in self.vol_history:
            return 0.5  # Neutral percentile
        
        # Get historical volatility values
        cutoff_date = datetime.now() - timedelta(days=window_days)
        historical_vols = [
            vol for date, vol in self.vol_history[symbol] 
            if date >= cutoff_date
        ]
        
        if len(historical_vols) < 10:
            return 0.5
        
        # Calculate percentile rank
        below_current = sum(1 for vol in historical_vols if vol < current_vol)
        percentile = below_current / len(historical_vols)
        
        return percentile
    
    def _classify_vol_regime(self, percentile: float) -> Tuple[VolatilityRegime, float]:
        """Classify volatility regime based on historical percentile"""
        thresholds = self.config['regime_thresholds']
        
        # Determine regime
        if percentile <= thresholds['ultra_low']:
            regime = VolatilityRegime.ULTRA_LOW
        elif percentile <= thresholds['low']:
            regime = VolatilityRegime.LOW
        elif percentile <= thresholds['elevated']:
            regime = VolatilityRegime.NORMAL
        elif percentile <= thresholds['high']:
            regime = VolatilityRegime.ELEVATED
        elif percentile <= thresholds['extreme']:
            regime = VolatilityRegime.HIGH
        else:
            regime = VolatilityRegime.EXTREME
        
        # Calculate confidence based on distance from boundaries
        confidence = self._calculate_regime_confidence(percentile, regime)
        
        return regime, confidence
    
    def _calculate_regime_confidence(self, percentile: float, regime: VolatilityRegime) -> float:
        """Calculate confidence in regime classification"""
        thresholds = self.config['regime_thresholds']
        
        if regime == VolatilityRegime.ULTRA_LOW:
            distance = thresholds['ultra_low'] - percentile
            confidence = min(1.0, distance * 20)  # Scale factor
        elif regime == VolatilityRegime.EXTREME:
            distance = percentile - thresholds['extreme']
            confidence = min(1.0, distance * 20)
        else:
            # For middle regimes, calculate distance to nearest boundary
            if regime == VolatilityRegime.LOW:
                lower, upper = thresholds['ultra_low'], thresholds['low']
            elif regime == VolatilityRegime.NORMAL:
                lower, upper = thresholds['low'], thresholds['elevated']
            elif regime == VolatilityRegime.ELEVATED:
                lower, upper = thresholds['elevated'], thresholds['high']
            else:  # HIGH
                lower, upper = thresholds['high'], thresholds['extreme']
            
            center = (lower + upper) / 2
            width = upper - lower
            distance_from_center = abs(percentile - center)
            confidence = max(0.1, 1.0 - (distance_from_center / (width / 2)))
        
        return confidence
    
    def _forecast_volatility(self, prices: List[float]) -> Dict[str, float]:
        """Forecast volatility using multiple models"""
        if len(prices) < 20:
            current_vol = self._calculate_realized_volatility(prices)
            return {
                '1d': current_vol,
                '5d': current_vol,
                '30d': current_vol,
                'confidence': 0.3
            }
        
        # Calculate different volatility measures
        realized_vol = self._calculate_realized_volatility(prices[-20:])
        ewma_vol = self._calculate_ewma_volatility(prices[-30:])
        garch_vol = self._calculate_garch_volatility(prices[-60:] if len(prices) >= 60 else prices)
        
        # Simple ensemble forecast
        vol_1d = (realized_vol * 0.5 + ewma_vol * 0.3 + garch_vol * 0.2)
        vol_5d = (realized_vol * 0.3 + ewma_vol * 0.4 + garch_vol * 0.3)
        vol_30d = (realized_vol * 0.2 + ewma_vol * 0.3 + garch_vol * 0.5)
        
        # Calculate forecast confidence based on model agreement
        models = [realized_vol, ewma_vol, garch_vol]
        model_std = statistics.stdev(models) if len(models) > 1 else 0
        model_mean = statistics.mean(models)
        confidence = max(0.1, 1.0 - (model_std / model_mean) if model_mean > 0 else 0.1)
        
        return {
            '1d': vol_1d,
            '5d': vol_5d,
            '30d': vol_30d,
            'confidence': confidence
        }
    
    def _analyze_vol_trend(self, symbol: str) -> VolatilityTrend:
        """Analyze recent volatility trend"""
        if symbol not in self.vol_history or len(self.vol_history[symbol]) < 10:
            return VolatilityTrend.STABLE
        
        # Get recent volatility values
        recent_vols = [vol for _, vol in self.vol_history[symbol][-10:]]
        
        if len(recent_vols) < 5:
            return VolatilityTrend.STABLE
        
        # Calculate trend slope
        x = list(range(len(recent_vols)))
        n = len(recent_vols)
        
        # Linear regression slope
        sum_x = sum(x)
        sum_y = sum(recent_vols)
        sum_xy = sum(x[i] * recent_vols[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if n * sum_x2 != sum_x ** 2 else 0
        
        # Classify trend based on slope
        vol_mean = statistics.mean(recent_vols)
        relative_slope = slope / vol_mean if vol_mean > 0 else 0
        
        if relative_slope > 0.1:
            return VolatilityTrend.SPIKING
        elif relative_slope > 0.02:
            return VolatilityTrend.RISING
        elif relative_slope < -0.02:
            return VolatilityTrend.DECLINING
        else:
            return VolatilityTrend.STABLE
    
    def _calculate_vol_risk_premium(self, implied_vol: float, realized_vol: float) -> float:
        """Calculate volatility risk premium (IV - RV)"""
        return implied_vol - realized_vol
    
    def _calculate_uncertainty_index(self, symbol: str) -> float:
        """Calculate market uncertainty index based on volatility dispersion"""
        if symbol not in self.vol_history or len(self.vol_history[symbol]) < 20:
            return 0.5
        
        # Get recent volatility values
        recent_vols = [vol for _, vol in self.vol_history[symbol][-20:]]
        
        # Calculate coefficient of variation
        vol_mean = statistics.mean(recent_vols)
        vol_std = statistics.stdev(recent_vols)
        
        uncertainty = (vol_std / vol_mean) if vol_mean > 0 else 0
        
        # Normalize to 0-1 scale
        return min(1.0, uncertainty * 2)
    
    def _calculate_tail_risk_indicator(self, prices: List[float]) -> float:
        """Calculate tail risk based on extreme price movements"""
        if len(prices) < 20:
            return 0.0
        
        # Calculate returns
        returns = [math.log(prices[i] / prices[i-1]) for i in range(1, len(prices)) if prices[i-1] > 0]
        
        if not returns:
            return 0.0
        
        # Calculate tail risk metrics
        returns_std = statistics.stdev(returns)
        extreme_threshold = 2 * returns_std  # 2 standard deviations
        
        extreme_moves = [r for r in returns if abs(r) > extreme_threshold]
        tail_frequency = len(extreme_moves) / len(returns)
        
        return min(1.0, tail_frequency * 10)  # Scale to 0-1
    
    def _update_price_history(self, symbol: str, price: float, timestamp: datetime):
        """Update internal price history"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append((timestamp, price))
        
        # Keep only recent history (1 year max)
        cutoff_date = timestamp - timedelta(days=365)
        self.price_history[symbol] = [
            (date, price) for date, price in self.price_history[symbol]
            if date >= cutoff_date
        ]
    
    def _get_price_history(self, symbol: str) -> List[float]:
        """Get price history for symbol"""
        if symbol not in self.price_history:
            return []
        return [price for _, price in self.price_history[symbol]]
    
    def _create_default_metrics(self, symbol: str, timestamp: datetime) -> VolatilityMetrics:
        """Create default volatility metrics when analysis fails"""
        return VolatilityMetrics(
            symbol=symbol,
            timestamp=timestamp,
            realized_vol_daily=15.0,  # Default assumption
            realized_vol_weekly=18.0,
            realized_vol_monthly=20.0,
            implied_vol_current=20.0,
            vol_percentile_30d=0.5,
            vol_percentile_90d=0.5,
            vol_percentile_1y=0.5,
            current_regime=VolatilityRegime.NORMAL,
            regime_confidence=0.3,
            regime_stability=0.5
        )
    
    def _calculate_regime_stability(self, symbol: str) -> float:
        """Calculate stability of current volatility regime"""
        # Simplified implementation - in reality would track regime changes
        return 0.75  # Placeholder
    
    def _calculate_vol_acceleration(self, symbol: str) -> float:
        """Calculate volatility acceleration (rate of change of volatility trend)"""
        # Simplified implementation
        return 0.0  # Placeholder
    
    def _calculate_mean_reversion_speed(self, symbol: str) -> float:
        """Calculate speed of volatility mean reversion"""
        # Simplified implementation using half-life concept
        return 0.05  # Placeholder - 5% daily mean reversion
    
    def _analyze_vol_term_structure(self, market_data: MarketData) -> Dict[str, float]:
        """Analyze volatility term structure (if options data available)"""
        # Placeholder - would require options data across different expiries
        return {
            "1M": market_data.iv,
            "2M": market_data.iv * 1.02,
            "3M": market_data.iv * 1.05
        }
    
    def _calculate_vol_skew(self, market_data: MarketData) -> float:
        """Calculate volatility skew measure"""
        # Placeholder - would require options data across different strikes
        return 0.0
    
    def get_volatility_summary(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive volatility summary for symbol"""
        if symbol not in self.vol_history or not self.vol_history[symbol]:
            return {"error": "No volatility history available"}
        
        recent_vols = [vol for _, vol in self.vol_history[symbol][-30:]]
        if not recent_vols:
            return {"error": "No recent volatility data"}
        
        return {
            "symbol": symbol,
            "current_vol": recent_vols[-1] if recent_vols else 0,
            "30d_average": statistics.mean(recent_vols),
            "30d_std": statistics.stdev(recent_vols) if len(recent_vols) > 1 else 0,
            "vol_trend": self._analyze_vol_trend(symbol).value,
            "data_points": len(recent_vols)
        }