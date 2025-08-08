from typing import List, Optional
from datetime import datetime, timedelta
import math

from ..base_strategy import (
    BaseStrategy, StrategySignal, MarketData, OptionLeg, 
    OptionType, OrderType, StrategyType
)


class ButterflySpreadStrategy(BaseStrategy):
    """
    Butterfly Spread Strategy (Conservative)
    
    Neutral strategy expecting low volatility around a specific price.
    Structure: Buy low strike, Sell 2x middle strike, Buy high strike (all calls or all puts)
    
    Market View: Expects low volatility, price to stay near middle strike
    Max Profit: (Middle strike - Low strike) - Net premium paid
    Max Loss: Net premium paid
    """
    
    def __init__(self):
        super().__init__("Butterfly Spread", StrategyType.CONSERVATIVE)
        
        # Strategy specific parameters
        self.wing_width = 100  # Points between strikes
        self.max_premium_paid = 40  # Maximum net debit
        self.max_loss_percentage = 0.01  # Max 1% of capital per trade (very conservative)
        self.target_dte = 20  # Prefer shorter expiry for precise targeting
        self.min_iv_percentile = 20  # Works in medium IV
        self.max_iv_percentile = 45  # Don't use in very high IV
        self.profit_target = 0.8  # Take profit at 80% of max profit
        self.stop_loss = 0.5  # Stop loss at 50% of premium paid
        self.max_distance_from_atm = 0.01  # Maximum 1% away from ATM for center strike
        
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        if not self._is_market_suitable_for_butterfly(market_data):
            return []
        
        signals = []
        
        try:
            if "NIFTY" in market_data.symbol or "BANKNIFTY" in market_data.symbol:
                # Try both call and put butterflies
                call_signal = await self._create_butterfly_signal(market_data, OptionType.CALL)
                if call_signal:
                    signals.append(call_signal)
                
                put_signal = await self._create_butterfly_signal(market_data, OptionType.PUT)
                if put_signal:
                    signals.append(put_signal)
                    
        except Exception as e:
            print(f"Error generating Butterfly Spread signals: {e}")
            
        return signals
    
    async def _create_butterfly_signal(self, market_data: MarketData, option_type: OptionType) -> Optional[StrategySignal]:
        spot_price = market_data.spot_price
        underlying = market_data.symbol
        
        # Strike interval based on underlying
        strike_interval = 50 if underlying == "NIFTY" else 100
        
        # Center strike should be close to ATM
        center_strike = round(spot_price / strike_interval) * strike_interval
        
        # Check if center strike is close enough to current price
        if abs(center_strike - spot_price) > spot_price * self.max_distance_from_atm:
            return None
        
        # Calculate wing strikes
        lower_strike = center_strike - self.wing_width
        upper_strike = center_strike + self.wing_width
        
        # Create the three legs of Butterfly Spread
        strategy_name = f"{option_type.value} Butterfly Spread"
        
        legs = [
            # Buy lower strike
            OptionLeg(
                strike_price=lower_strike,
                option_type=option_type,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(lower_strike, spot_price, option_type, market_data.iv)
            ),
            # Sell 2x center strike
            OptionLeg(
                strike_price=center_strike,
                option_type=option_type,
                order_type=OrderType.SELL,
                quantity=2,
                premium=self._estimate_premium(center_strike, spot_price, option_type, market_data.iv)
            ),
            # Buy upper strike
            OptionLeg(
                strike_price=upper_strike,
                option_type=option_type,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(upper_strike, spot_price, option_type, market_data.iv)
            )
        ]
        
        # Calculate net premium (debit paid)
        net_premium = (legs[0].premium + legs[2].premium) - (2 * legs[1].premium)
        
        # Check if premium is within acceptable range
        if net_premium > self.max_premium_paid or net_premium <= 0:
            return None
        
        # Calculate max profit and loss
        max_profit = self.wing_width - net_premium
        max_loss = net_premium
        
        # Calculate breakeven points
        if option_type == OptionType.CALL:
            lower_breakeven = lower_strike + net_premium
            upper_breakeven = upper_strike - net_premium
        else:  # PUT
            lower_breakeven = lower_strike + net_premium
            upper_breakeven = upper_strike - net_premium
        
        # Calculate probability of profit (staying between breakevens)
        probability_of_profit = self._calculate_butterfly_pop(
            spot_price, lower_breakeven, upper_breakeven, market_data
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            market_data, net_premium, probability_of_profit, max_profit/max_loss
        )
        
        if confidence_score < self.min_confidence:
            return None
        
        # Create expiry date
        expiry_date = datetime.now() + timedelta(days=self.target_dte)
        
        signal = StrategySignal(
            strategy_name=strategy_name,
            symbol=underlying,
            legs=legs,
            max_profit=max_profit,
            max_loss=max_loss,
            breakeven_points=[lower_breakeven, upper_breakeven],
            probability_of_profit=probability_of_profit,
            confidence_score=confidence_score,
            expiry_date=expiry_date
        )
        
        return signal
    
    def _is_market_suitable_for_butterfly(self, market_data: MarketData) -> bool:
        # Skip market hours check for testing
        
        # Check IV levels (works in medium IV environments)
        if market_data.iv < self.min_iv_percentile or market_data.iv > self.max_iv_percentile:
            return False
        
        # Check volume
        if market_data.volume < 150000:
            return False
        
        # Butterfly works best when we expect low volatility
        return True
    
    def _calculate_butterfly_pop(self, spot: float, lower_be: float, 
                                upper_be: float, market_data: MarketData) -> float:
        # Probability of staying between breakevens (profit zone)
        profit_range = upper_be - lower_be
        
        # Expected move based on IV
        expected_move = spot * (market_data.iv / 100) * math.sqrt(self.target_dte / 365)
        
        # Higher probability if profit range is wider than expected move
        if expected_move <= 0:
            return 0.6
        
        prob = min(0.85, 0.4 + (profit_range / (expected_move * 2)))
        return max(prob, 0.3)  # Minimum 30% probability
    
    def _estimate_premium(self, strike: float, spot: float, option_type: OptionType, iv: float) -> float:
        # Premium estimation for butterfly legs
        points_from_atm = abs(strike - spot)
        
        base_time_value = iv * 0.3 * math.sqrt(self.target_dte/365)
        
        # Intrinsic value
        if option_type == OptionType.CALL:
            intrinsic = max(0, spot - strike)
        else:  # PUT  
            intrinsic = max(0, strike - spot)
        
        # Time value based on distance from ATM
        if points_from_atm <= 50:  # Very close to ATM
            time_value = base_time_value * 100
        elif points_from_atm <= 100:  # Wing strikes
            time_value = base_time_value * 70
        else:  # Far from ATM
            time_value = base_time_value * 40
        
        premium = intrinsic + time_value
        
        # Minimum premium
        premium = max(premium, 20.0 if points_from_atm <= 50 else 12.0)
        
        return round(premium, 2)
    
    def _calculate_confidence_score(self, market_data: MarketData, net_premium: float, 
                                  pop: float, risk_reward_ratio: float) -> float:
        score = 0.0
        
        # IV component (25% weight) - medium IV is best
        optimal_iv = 32
        iv_score = max(0.3, 1.0 - abs(market_data.iv - optimal_iv) / optimal_iv)
        score += iv_score * 0.25
        
        # Cost efficiency component (25% weight) - lower cost is better
        cost_score = max(0.2, 1.0 - (net_premium / self.max_premium_paid))
        score += cost_score * 0.25
        
        # Probability of profit component (30% weight)
        score += pop * 0.3
        
        # Risk-reward ratio component (20% weight)
        rr_score = min(risk_reward_ratio / 4.0, 1.0)  # Target 4:1 or better
        score += rr_score * 0.2
        
        return min(score, 0.92)
    
    def validate_signal(self, signal: StrategySignal, current_positions: int) -> bool:
        # Check position limits
        if current_positions >= self.max_positions:
            return False
        
        # Check confidence threshold
        if signal.confidence_score < self.min_confidence:
            return False
        
        # Check max loss vs capital
        if signal.max_loss > (self.max_loss_percentage * 100000):
            return False
        
        # Validate Butterfly Spread structure (3 legs, specific pattern)
        if len(signal.legs) != 3:
            return False
        
        # Check that all legs are same option type
        option_types = set(leg.option_type for leg in signal.legs)
        if len(option_types) != 1:
            return False
        
        # Check quantities (1-2-1 pattern)
        quantities = [leg.quantity for leg in signal.legs]
        if sorted(quantities) != [1, 1, 2]:
            return False
        
        # Check strikes are in order and equally spaced
        strikes = sorted([leg.strike_price for leg in signal.legs])
        if not (strikes[1] - strikes[0] == strikes[2] - strikes[1]):
            return False
        
        return True
    
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        # Very conservative position sizing for butterfly spreads
        max_risk_per_trade = available_capital * self.max_loss_percentage
        
        # Calculate lots based on max loss per lot (net premium paid)
        max_loss_per_lot = signal.max_loss
        max_lots = int(max_risk_per_trade / max_loss_per_lot) if max_loss_per_lot > 0 else 1
        
        # Conservative sizing for precise strategies
        return min(max_lots, 2) if max_lots > 0 else 1