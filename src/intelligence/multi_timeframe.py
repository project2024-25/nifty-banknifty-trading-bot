"""
Multi-Timeframe Analysis Engine for Sophisticated Trading System

This module provides comprehensive multi-timeframe analysis combining technical indicators,
market structure analysis, and sophisticated signal generation across multiple timeframes.
Works with Kite Connect API for real market data.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import math

try:
    import pandas as pd
    import numpy as np
    from scipy import stats
except ImportError:
    pd = None
    np = None
    stats = None

logger = logging.getLogger(__name__)


@dataclass
class TimeframeSignal:
    """Individual timeframe signal."""
    timeframe: str
    timestamp: datetime
    trend: str  # bullish, bearish, sideways
    strength: float  # 0-1
    support: Optional[float]
    resistance: Optional[float]
    indicators: Dict[str, Any]
    confidence: float  # 0-1
    volume_profile: Dict[str, float]


@dataclass
class MultiTimeframeAnalysis:
    """Complete multi-timeframe analysis result."""
    symbol: str
    timestamp: datetime
    overall_trend: str
    overall_confidence: float
    timeframes: Dict[str, TimeframeSignal]
    entry_zones: List[Dict[str, Any]]
    risk_levels: Dict[str, float]
    recommendations: List[str]
    market_regime: str


class TechnicalIndicators:
    """Technical indicator calculations."""
    
    @staticmethod
    def ema(data: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(data) < period:
            return sum(data) / len(data) if data else 0
        
        alpha = 2 / (period + 1)
        ema_val = data[0]
        
        for price in data[1:]:
            ema_val = (price * alpha) + (ema_val * (1 - alpha))
        
        return ema_val
    
    @staticmethod
    def rsi(data: List[float], period: int = 14) -> float:
        """Calculate RSI."""
        if len(data) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD."""
        if len(data) < slow:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        fast_ema = TechnicalIndicators.ema(data, fast)
        slow_ema = TechnicalIndicators.ema(data, slow)
        macd_line = fast_ema - slow_ema
        
        # Simplified signal line (would need more data points for proper calculation)
        signal_line = macd_line * 0.9  # Approximation
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def bollinger_bands(data: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands."""
        if len(data) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'position': 0.5}
        
        recent_data = data[-period:]
        middle = sum(recent_data) / len(recent_data)
        
        variance = sum((x - middle) ** 2 for x in recent_data) / len(recent_data)
        std = variance ** 0.5
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        current_price = data[-1]
        position = (current_price - lower) / (upper - lower) if upper != lower else 0.5
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'position': min(max(position, 0), 1)
        }


class MultiTimeframeAnalyzer:
    """
    Advanced multi-timeframe analysis engine.
    
    Analyzes market conditions across multiple timeframes and provides
    sophisticated signals for the trading system.
    """
    
    TIMEFRAMES = {
        '5min': {'period': 5, 'bars_needed': 100},
        '15min': {'period': 15, 'bars_needed': 100},
        '1hour': {'period': 60, 'bars_needed': 50},
        'daily': {'period': 1440, 'bars_needed': 30},
        'weekly': {'period': 10080, 'bars_needed': 20}
    }
    
    def __init__(self, kite_wrapper=None):
        """
        Initialize multi-timeframe analyzer.
        
        Args:
            kite_wrapper: KiteConnect wrapper for real market data
        """
        self.kite_wrapper = kite_wrapper
        self.cache = {}
        self.cache_expiry = {}
        
    async def analyze_symbol(self, symbol: str, use_real_data: bool = False) -> MultiTimeframeAnalysis:
        """
        Perform comprehensive multi-timeframe analysis.
        
        Args:
            symbol: Trading symbol to analyze
            use_real_data: Whether to use real Kite Connect data
            
        Returns:
            Complete multi-timeframe analysis
        """
        logger.info(f"Starting multi-timeframe analysis for {symbol}")
        
        try:
            # Get data for all timeframes
            timeframe_data = {}
            
            for tf_name, tf_config in self.TIMEFRAMES.items():
                if use_real_data and self.kite_wrapper:
                    data = await self._get_real_data(symbol, tf_name, tf_config['bars_needed'])
                else:
                    data = await self._get_mock_data(symbol, tf_name, tf_config['bars_needed'])
                
                timeframe_data[tf_name] = data
            
            # Analyze each timeframe
            timeframe_signals = {}
            
            for tf_name, data in timeframe_data.items():
                signal = await self._analyze_timeframe(symbol, tf_name, data)
                timeframe_signals[tf_name] = signal
            
            # Aggregate signals across timeframes
            analysis = await self._aggregate_analysis(symbol, timeframe_signals)
            
            logger.info(f"✅ Multi-timeframe analysis complete for {symbol}: {analysis.overall_trend} "
                       f"(confidence: {analysis.overall_confidence:.2f})")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Multi-timeframe analysis failed for {symbol}: {e}")
            return await self._get_fallback_analysis(symbol)
    
    async def _get_real_data(self, symbol: str, timeframe: str, bars: int) -> List[Dict[str, Any]]:
        """Get real market data from Kite Connect."""
        try:
            # Check cache first
            cache_key = f"{symbol}_{timeframe}"
            if (cache_key in self.cache and 
                cache_key in self.cache_expiry and 
                datetime.now() < self.cache_expiry[cache_key]):
                return self.cache[cache_key]
            
            # Get historical data from Kite
            if hasattr(self.kite_wrapper, 'get_historical_data'):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)  # Get 30 days of data
                
                historical_data = await self.kite_wrapper.get_historical_data(
                    symbol, start_date, end_date, timeframe
                )
                
                if historical_data:
                    # Cache for 5 minutes
                    self.cache[cache_key] = historical_data
                    self.cache_expiry[cache_key] = datetime.now() + timedelta(minutes=5)
                    return historical_data
            
            # Fallback to current quote
            quotes = await self.kite_wrapper.get_quote([symbol])
            if symbol in quotes:
                price = quotes[symbol].get('last_price', 100)
                return await self._generate_mock_historical_data(price, bars)
            
        except Exception as e:
            logger.warning(f"Failed to get real data for {symbol}: {e}")
        
        # Fallback to mock data
        return await self._get_mock_data(symbol, timeframe, bars)
    
    async def _get_mock_data(self, symbol: str, timeframe: str, bars: int) -> List[Dict[str, Any]]:
        """Generate realistic mock OHLCV data."""
        base_price = 25000 if 'NIFTY' in symbol else 52000 if 'BANKNIFTY' in symbol else 100
        
        # For options, use premium pricing
        if 'CE' in symbol or 'PE' in symbol:
            base_price = base_price * 0.01  # ~1% as option premium
        
        return await self._generate_mock_historical_data(base_price, bars)
    
    async def _generate_mock_historical_data(self, base_price: float, bars: int) -> List[Dict[str, Any]]:
        """Generate realistic historical OHLCV data."""
        data = []
        current_price = base_price
        
        for i in range(bars):
            # Generate realistic price movement
            change_percent = (hash(f"{base_price}_{i}") % 200 - 100) / 10000  # ±1% max
            
            open_price = current_price
            change = open_price * change_percent
            
            high = open_price + abs(change) * 1.5
            low = open_price - abs(change) * 1.5
            close_price = open_price + change
            
            volume = 100000 + (hash(f"vol_{i}") % 50000)
            
            data.append({
                'timestamp': datetime.now() - timedelta(minutes=(bars-i)*5),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
            
            current_price = close_price
        
        return data
    
    async def _analyze_timeframe(self, symbol: str, timeframe: str, data: List[Dict[str, Any]]) -> TimeframeSignal:
        """Analyze individual timeframe."""
        if not data:
            return TimeframeSignal(
                timeframe=timeframe,
                timestamp=datetime.now(),
                trend='sideways',
                strength=0.5,
                support=None,
                resistance=None,
                indicators={},
                confidence=0.3,
                volume_profile={}
            )
        
        # Extract price data
        closes = [candle['close'] for candle in data]
        highs = [candle['high'] for candle in data]
        lows = [candle['low'] for candle in data]
        volumes = [candle['volume'] for candle in data]
        
        # Calculate technical indicators
        indicators = {}
        
        # EMA analysis
        ema_20 = TechnicalIndicators.ema(closes, 20)
        ema_50 = TechnicalIndicators.ema(closes, 50)
        indicators['ema_20'] = ema_20
        indicators['ema_50'] = ema_50
        
        # RSI
        rsi = TechnicalIndicators.rsi(closes)
        indicators['rsi'] = rsi
        
        # MACD
        macd_data = TechnicalIndicators.macd(closes)
        indicators.update(macd_data)
        
        # Bollinger Bands
        bb_data = TechnicalIndicators.bollinger_bands(closes)
        indicators.update(bb_data)
        
        # Determine trend
        current_price = closes[-1]
        trend = 'sideways'
        strength = 0.5
        
        if current_price > ema_20 > ema_50:
            trend = 'bullish'
            strength = min((current_price - ema_20) / ema_20 * 10, 1.0)
        elif current_price < ema_20 < ema_50:
            trend = 'bearish'
            strength = min((ema_20 - current_price) / ema_20 * 10, 1.0)
        
        # Support and resistance
        recent_highs = highs[-10:]
        recent_lows = lows[-10:]
        resistance = max(recent_highs) if recent_highs else current_price * 1.02
        support = min(recent_lows) if recent_lows else current_price * 0.98
        
        # Confidence calculation
        confidence = 0.5
        if abs(indicators['macd']) > abs(indicators['signal']):
            confidence += 0.2
        if 30 <= rsi <= 70:
            confidence += 0.2
        else:
            confidence += 0.1  # Extreme RSI can be good signal
        if abs(strength) > 0.3:
            confidence += 0.1
        
        confidence = min(confidence, 1.0)
        
        # Volume profile
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        current_volume = volumes[-1] if volumes else 0
        
        volume_profile = {
            'average': avg_volume,
            'current': current_volume,
            'ratio': current_volume / avg_volume if avg_volume > 0 else 1.0,
            'trend': 'increasing' if current_volume > avg_volume else 'decreasing'
        }
        
        return TimeframeSignal(
            timeframe=timeframe,
            timestamp=datetime.now(),
            trend=trend,
            strength=abs(strength),
            support=support,
            resistance=resistance,
            indicators=indicators,
            confidence=confidence,
            volume_profile=volume_profile
        )
    
    async def _aggregate_analysis(self, symbol: str, timeframe_signals: Dict[str, TimeframeSignal]) -> MultiTimeframeAnalysis:
        """Aggregate signals across timeframes."""
        
        # Weight timeframes by importance
        weights = {
            '5min': 0.1,
            '15min': 0.15,
            '1hour': 0.25,
            'daily': 0.35,
            'weekly': 0.15
        }
        
        # Calculate overall trend
        bullish_weight = 0
        bearish_weight = 0
        sideways_weight = 0
        total_confidence = 0
        
        for tf_name, signal in timeframe_signals.items():
            weight = weights.get(tf_name, 0.1)
            weighted_confidence = signal.confidence * weight
            
            if signal.trend == 'bullish':
                bullish_weight += weighted_confidence
            elif signal.trend == 'bearish':
                bearish_weight += weighted_confidence
            else:
                sideways_weight += weighted_confidence
            
            total_confidence += weighted_confidence
        
        # Determine overall trend
        if bullish_weight > bearish_weight and bullish_weight > sideways_weight:
            overall_trend = 'bullish'
            overall_confidence = bullish_weight
        elif bearish_weight > bullish_weight and bearish_weight > sideways_weight:
            overall_trend = 'bearish'
            overall_confidence = bearish_weight
        else:
            overall_trend = 'sideways'
            overall_confidence = sideways_weight
        
        overall_confidence = min(overall_confidence / max(sum(weights.values()), 0.1), 1.0)
        
        # Generate entry zones
        entry_zones = await self._generate_entry_zones(timeframe_signals)
        
        # Calculate risk levels
        risk_levels = await self._calculate_risk_levels(timeframe_signals)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(overall_trend, overall_confidence, timeframe_signals)
        
        # Determine market regime
        market_regime = await self._determine_market_regime(timeframe_signals)
        
        return MultiTimeframeAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            overall_trend=overall_trend,
            overall_confidence=overall_confidence,
            timeframes=timeframe_signals,
            entry_zones=entry_zones,
            risk_levels=risk_levels,
            recommendations=recommendations,
            market_regime=market_regime
        )
    
    async def _generate_entry_zones(self, signals: Dict[str, TimeframeSignal]) -> List[Dict[str, Any]]:
        """Generate potential entry zones."""
        entry_zones = []
        
        # Use daily and hourly signals for main entry zones
        if 'daily' in signals and '1hour' in signals:
            daily_signal = signals['daily']
            hourly_signal = signals['1hour']
            
            if daily_signal.trend == hourly_signal.trend and daily_signal.confidence > 0.6:
                zone_type = 'momentum' if daily_signal.trend != 'sideways' else 'range'
                
                entry_zones.append({
                    'type': zone_type,
                    'trend': daily_signal.trend,
                    'entry_min': daily_signal.support if daily_signal.trend == 'bullish' else daily_signal.resistance,
                    'entry_max': daily_signal.resistance if daily_signal.trend == 'bullish' else daily_signal.support,
                    'confidence': (daily_signal.confidence + hourly_signal.confidence) / 2,
                    'timeframe_alignment': True
                })
        
        # Add scalping zones from 5min and 15min
        if '5min' in signals and '15min' in signals:
            scalp_5m = signals['5min']
            scalp_15m = signals['15min']
            
            if scalp_5m.confidence > 0.7 or scalp_15m.confidence > 0.7:
                entry_zones.append({
                    'type': 'scalping',
                    'trend': scalp_5m.trend,
                    'entry_min': min(scalp_5m.support or 0, scalp_15m.support or 0),
                    'entry_max': max(scalp_5m.resistance or 0, scalp_15m.resistance or 0),
                    'confidence': max(scalp_5m.confidence, scalp_15m.confidence),
                    'timeframe_alignment': scalp_5m.trend == scalp_15m.trend
                })
        
        return entry_zones
    
    async def _calculate_risk_levels(self, signals: Dict[str, TimeframeSignal]) -> Dict[str, float]:
        """Calculate risk management levels."""
        risk_levels = {
            'stop_loss': 0.02,  # 2% default
            'take_profit': 0.04,  # 4% default
            'position_size': 0.1  # 10% default
        }
        
        # Adjust based on volatility and confidence
        if 'daily' in signals:
            daily_signal = signals['daily']
            
            # Higher confidence = tighter stops, larger positions
            if daily_signal.confidence > 0.8:
                risk_levels['stop_loss'] *= 0.8
                risk_levels['position_size'] *= 1.2
            elif daily_signal.confidence < 0.4:
                risk_levels['stop_loss'] *= 1.5
                risk_levels['position_size'] *= 0.7
            
            # Adjust for volatility (using Bollinger Band position as proxy)
            bb_position = daily_signal.indicators.get('position', 0.5)
            if bb_position > 0.8 or bb_position < 0.2:  # High volatility
                risk_levels['stop_loss'] *= 1.3
                risk_levels['take_profit'] *= 1.5
        
        # Ensure reasonable bounds
        risk_levels['stop_loss'] = max(0.005, min(risk_levels['stop_loss'], 0.05))  # 0.5% - 5%
        risk_levels['take_profit'] = max(0.01, min(risk_levels['take_profit'], 0.10))  # 1% - 10%
        risk_levels['position_size'] = max(0.02, min(risk_levels['position_size'], 0.20))  # 2% - 20%
        
        return risk_levels
    
    async def _generate_recommendations(self, trend: str, confidence: float, 
                                      signals: Dict[str, TimeframeSignal]) -> List[str]:
        """Generate trading recommendations."""
        recommendations = []
        
        # Overall market recommendation
        if confidence > 0.7:
            if trend == 'bullish':
                recommendations.append("🟢 Strong bullish signal - Consider aggressive long positions")
            elif trend == 'bearish':
                recommendations.append("🔴 Strong bearish signal - Consider aggressive short positions")
            else:
                recommendations.append("🟡 Strong sideways signal - Consider range trading strategies")
        elif confidence > 0.5:
            recommendations.append(f"⚡ Moderate {trend} signal - Use conservative position sizing")
        else:
            recommendations.append("⚠️ Low confidence signal - Consider staying in cash or very small positions")
        
        # Timeframe specific recommendations
        if '5min' in signals and signals['5min'].confidence > 0.8:
            recommendations.append("⚡ Strong intraday momentum - Good for scalping")
        
        if 'daily' in signals and signals['daily'].confidence > 0.7:
            recommendations.append(f"📊 Daily trend confirmed: {signals['daily'].trend}")
        
        # Risk management recommendations
        if any(s.indicators.get('rsi', 50) > 80 for s in signals.values()):
            recommendations.append("⚠️ Overbought conditions detected - Consider taking profits")
        elif any(s.indicators.get('rsi', 50) < 20 for s in signals.values()):
            recommendations.append("💡 Oversold conditions detected - Potential buying opportunity")
        
        return recommendations
    
    async def _determine_market_regime(self, signals: Dict[str, TimeframeSignal]) -> str:
        """Determine current market regime."""
        if 'daily' not in signals:
            return 'uncertain'
        
        daily_signal = signals['daily']
        rsi = daily_signal.indicators.get('rsi', 50)
        bb_position = daily_signal.indicators.get('position', 0.5)
        
        # High volatility regime
        if bb_position > 0.9 or bb_position < 0.1:
            if daily_signal.trend == 'bullish':
                return 'bull_volatile'
            elif daily_signal.trend == 'bearish':
                return 'bear_volatile'
            else:
                return 'high_volatility'
        
        # Trending regimes
        if daily_signal.confidence > 0.7:
            if daily_signal.trend == 'bullish':
                return 'bull_trending'
            elif daily_signal.trend == 'bearish':
                return 'bear_trending'
        
        # Range-bound regime
        if 0.3 <= bb_position <= 0.7 and 40 <= rsi <= 60:
            return 'sideways'
        
        # Breakout pending
        if daily_signal.strength < 0.3 and daily_signal.confidence > 0.5:
            return 'breakout_pending'
        
        return 'mixed'
    
    async def _get_fallback_analysis(self, symbol: str) -> MultiTimeframeAnalysis:
        """Provide fallback analysis when main analysis fails."""
        logger.warning(f"Using fallback analysis for {symbol}")
        
        return MultiTimeframeAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            overall_trend='sideways',
            overall_confidence=0.3,
            timeframes={},
            entry_zones=[],
            risk_levels={
                'stop_loss': 0.02,
                'take_profit': 0.04,
                'position_size': 0.05
            },
            recommendations=["⚠️ Analysis unavailable - Use minimum position sizes"],
            market_regime='uncertain'
        )
    
    async def analyze_pre_market(self) -> Dict[str, Any]:
        """Perform pre-market analysis for both NIFTY and BANKNIFTY."""
        logger.info("🌅 Starting pre-market multi-timeframe analysis...")
        
        try:
            # Analyze both main instruments
            nifty_analysis = await self.analyze_symbol('NIFTY', use_real_data=True)
            banknifty_analysis = await self.analyze_symbol('BANKNIFTY', use_real_data=True)
            
            # Create comprehensive pre-market report
            report = {
                'timestamp': datetime.now().isoformat(),
                'market_status': 'pre_market',
                'nifty': asdict(nifty_analysis),
                'banknifty': asdict(banknifty_analysis),
                'market_outlook': self._generate_market_outlook(nifty_analysis, banknifty_analysis),
                'trading_plan': self._generate_trading_plan(nifty_analysis, banknifty_analysis)
            }
            
            logger.info("✅ Pre-market analysis completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Pre-market analysis failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'failed'
            }
    
    def _generate_market_outlook(self, nifty: MultiTimeframeAnalysis, banknifty: MultiTimeframeAnalysis) -> Dict[str, Any]:
        """Generate overall market outlook."""
        combined_confidence = (nifty.overall_confidence + banknifty.overall_confidence) / 2
        
        # Determine market correlation
        if nifty.overall_trend == banknifty.overall_trend:
            correlation = 'aligned'
        else:
            correlation = 'divergent'
        
        outlook = {
            'overall_sentiment': nifty.overall_trend if correlation == 'aligned' else 'mixed',
            'confidence': combined_confidence,
            'correlation': correlation,
            'dominant_regime': nifty.market_regime,
            'key_levels': {
                'nifty_support': nifty.timeframes.get('daily', {}).support if nifty.timeframes else None,
                'nifty_resistance': nifty.timeframes.get('daily', {}).resistance if nifty.timeframes else None,
                'banknifty_support': banknifty.timeframes.get('daily', {}).support if banknifty.timeframes else None,
                'banknifty_resistance': banknifty.timeframes.get('daily', {}).resistance if banknifty.timeframes else None,
            }
        }
        
        return outlook
    
    def _generate_trading_plan(self, nifty: MultiTimeframeAnalysis, banknifty: MultiTimeframeAnalysis) -> Dict[str, Any]:
        """Generate trading plan for the day."""
        plan = {
            'primary_instrument': 'NIFTY' if nifty.overall_confidence > banknifty.overall_confidence else 'BANKNIFTY',
            'strategy_bias': nifty.overall_trend,
            'risk_mode': 'aggressive' if (nifty.overall_confidence + banknifty.overall_confidence) / 2 > 0.7 else 'conservative',
            'entry_zones': nifty.entry_zones + banknifty.entry_zones,
            'key_recommendations': nifty.recommendations + banknifty.recommendations
        }
        
        return plan


# Example usage and testing
if __name__ == "__main__":
    async def test_analyzer():
        analyzer = MultiTimeframeAnalyzer()
        
        # Test NIFTY analysis
        analysis = await analyzer.analyze_symbol('NIFTY')
        print(f"NIFTY Analysis: {analysis.overall_trend} (confidence: {analysis.overall_confidence:.2f})")
        
        # Test pre-market analysis
        pre_market = await analyzer.analyze_pre_market()
        print(f"Pre-market outlook: {pre_market.get('market_outlook', {}).get('overall_sentiment')}")
    
    asyncio.run(test_analyzer())