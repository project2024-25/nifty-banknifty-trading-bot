from typing import List, Optional
from datetime import datetime, timedelta
import math

from ..base_strategy import (
    BaseStrategy, StrategySignal, MarketData, OptionLeg, 
    OptionType, OrderType, StrategyType
)


class BearPutSpreadStrategy(BaseStrategy):
    """
    Bear Put Spread Strategy (Conservative)
    
    Bearish strategy with limited risk and limited profit.
    Structure: Buy higher strike put, Sell lower strike put
    
    Market View: Moderately bearish
    Max Profit: (Strike difference - Net premium paid)
    Max Loss: Net premium paid
    """
    
    def __init__(self):
        super().__init__("Bear Put Spread", StrategyType.CONSERVATIVE)
        
        # Strategy specific parameters
        self.spread_width = 100  # Points between strikes
        self.max_premium_paid = 50  # Maximum net debit
        self.max_loss_percentage = 0.015  # Max 1.5% of capital per trade
        self.target_dte = 30  # Prefer monthly options for directional plays
        self.min_iv_percentile = 15  # Works in low to medium IV
        self.profit_target = 0.7  # Take profit at 70% of max profit
        self.stop_loss = 1.5  # Stop loss at 150% of premium paid
        self.max_moneyness = 0.03  # Maximum 3% ITM for long put
        
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        if not self._is_market_suitable_for_bear_put_spread(market_data):
            return []
        
        signals = []
        
        try:
            if "NIFTY" in market_data.symbol or "BANKNIFTY" in market_data.symbol:
                signal = await self._create_bear_put_spread_signal(market_data)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error generating Bear Put Spread signals: {e}")
            
        return signals
    
    async def _create_bear_put_spread_signal(self, market_data: MarketData) -> Optional[StrategySignal]:
        spot_price = market_data.spot_price
        underlying = market_data.symbol
        
        # Strike interval based on underlying
        strike_interval = 50 if underlying == "NIFTY" else 100
        
        # Calculate strikes for Bear Put Spread
        # Buy higher strike put (closer to ATM for directional benefit)
        # Sell lower strike put (to reduce cost)
        
        atm_strike = round(spot_price / strike_interval) * strike_interval
        
        # Long put strike (can be slightly ITM or ATM)
        max_itm_distance = spot_price * self.max_moneyness
        long_put_strike = min(atm_strike + max_itm_distance, atm_strike)
        long_put_strike = round(long_put_strike / strike_interval) * strike_interval
        
        # Short put strike (lower strike to cap profits and reduce cost)
        short_put_strike = long_put_strike - self.spread_width
        
        # Create the two legs of Bear Put Spread
        legs = [
            # Buy higher strike put (pay premium)
            OptionLeg(
                strike_price=long_put_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(long_put_strike, spot_price, OptionType.PUT, market_data.iv)
            ),
            # Sell lower strike put (collect premium to reduce cost)
            OptionLeg(
                strike_price=short_put_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.SELL,
                quantity=1,
                premium=self._estimate_premium(short_put_strike, spot_price, OptionType.PUT, market_data.iv)
            )
        ]
        
        # Calculate net premium (debit paid)
        net_premium = legs[0].premium - legs[1].premium
        
        # Check if premium is within acceptable range
        if net_premium > self.max_premium_paid or net_premium <= 0:
            return None
        
        # Calculate max profit and loss
        max_profit = self.spread_width - net_premium
        max_loss = net_premium
        
        # Calculate breakeven point
        breakeven_point = long_put_strike - net_premium
        
        # Calculate probability of profit (simplified)
        # Profit if spot goes below breakeven
        distance_from_spot = spot_price - breakeven_point
        probability_of_profit = max(0.4, 0.8 - (distance_from_spot / (spot_price * 0.05)))
        probability_of_profit = min(probability_of_profit, 0.85)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            market_data, net_premium, probability_of_profit, max_profit/max_loss
        )
        
        if confidence_score < self.min_confidence:
            return None
        
        # Create expiry date
        expiry_date = datetime.now() + timedelta(days=self.target_dte)
        
        signal = StrategySignal(
            strategy_name=self.name,
            symbol=underlying,
            legs=legs,
            max_profit=max_profit,
            max_loss=max_loss,
            breakeven_points=[breakeven_point],
            probability_of_profit=probability_of_profit,
            confidence_score=confidence_score,
            expiry_date=expiry_date
        )
        
        return signal
    
    def _is_market_suitable_for_bear_put_spread(self, market_data: MarketData) -> bool:
        # Skip market hours check for testing
        
        # Check IV levels (works better in lower to medium IV)
        if market_data.iv > 50:  # Too high IV makes it expensive
            return False
        
        # Check volume
        if market_data.volume < 100000:
            return False
        
        # Bear Put Spread works when we expect moderate downward movement
        return True
    
    def _estimate_premium(self, strike: float, spot: float, option_type: OptionType, iv: float) -> float:
        # Use the same premium estimation as other strategies
        points_from_atm = abs(strike - spot)
        
        base_time_value = iv * 0.3 * math.sqrt(self.target_dte/365)
        
        # Intrinsic value
        if option_type == OptionType.CALL:
            intrinsic = max(0, spot - strike)
        else:  # PUT  
            intrinsic = max(0, strike - spot)
        
        # Time value decreases with distance from ATM
        if points_from_atm <= 100:  # ATM/Near ATM
            time_value = base_time_value * 100  # Higher for ATM puts
        elif points_from_atm <= 200:  # Slightly OTM
            time_value = base_time_value * 60
        else:  # Far OTM
            time_value = base_time_value * 30
        
        premium = intrinsic + time_value
        
        # Minimum premium
        premium = max(premium, 15.0 if points_from_atm <= 100 else 8.0)
        
        return round(premium, 2)
    
    def _calculate_confidence_score(self, market_data: MarketData, net_premium: float, 
                                  pop: float, risk_reward_ratio: float) -> float:
        score = 0.0
        
        # IV component (20% weight) - lower IV is better for buying options
        iv_score = max(0.3, 1.0 - (market_data.iv / 60))  # Inverse relationship
        score += iv_score * 0.2
        
        # Cost efficiency component (30% weight) - lower cost is better
        cost_score = max(0.2, 1.0 - (net_premium / self.max_premium_paid))
        score += cost_score * 0.3
        
        # Probability of profit component (30% weight)
        score += pop * 0.3
        
        # Risk-reward ratio component (20% weight)
        rr_score = min(risk_reward_ratio / 3.0, 1.0)  # Target 3:1 or better
        score += rr_score * 0.2
        
        return min(score, 0.95)
    
    def validate_signal(self, signal: StrategySignal, current_positions: int) -> bool:
        # Check position limits
        if current_positions >= self.max_positions:
            return False
        
        # Check confidence threshold
        if signal.confidence_score < self.min_confidence:
            return False
        
        # Check max loss vs capital (net premium paid)
        if signal.max_loss > (self.max_loss_percentage * 100000):
            return False
        
        # Validate Bear Put Spread structure (2 legs, both puts)
        if len(signal.legs) != 2:
            return False
        
        puts = [leg for leg in signal.legs if leg.option_type == OptionType.PUT]
        if len(puts) != 2:
            return False
        
        # Check that we have one buy and one sell
        buys = [leg for leg in signal.legs if leg.order_type == OrderType.BUY]
        sells = [leg for leg in signal.legs if leg.order_type == OrderType.SELL]
        
        if len(buys) != 1 or len(sells) != 1:
            return False
        
        # Check that long put has higher strike than short put
        long_put = buys[0]
        short_put = sells[0]
        if long_put.strike_price <= short_put.strike_price:
            return False
        
        return True
    
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        # Position sizing based on premium paid (max loss)
        max_risk_per_trade = available_capital * self.max_loss_percentage
        
        # Calculate lots based on max loss per lot (premium paid)
        max_loss_per_lot = signal.max_loss
        max_lots = int(max_risk_per_trade / max_loss_per_lot) if max_loss_per_lot > 0 else 1
        
        # Conservative sizing for directional spreads
        return min(max_lots, 3) if max_lots > 0 else 1