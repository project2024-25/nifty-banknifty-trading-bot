from typing import List, Optional
from datetime import datetime, timedelta
import math

from ..base_strategy import (
    BaseStrategy, StrategySignal, MarketData, OptionLeg, 
    OptionType, OrderType, StrategyType
)


class LongStraddleStrategy(BaseStrategy):
    """
    Long Straddle Strategy (Aggressive)
    
    Volatility strategy expecting large price movement in either direction.
    Structure: Buy ATM call + Buy ATM put
    
    Market View: Expects high volatility (direction agnostic)
    Max Profit: Unlimited (theoretically)
    Max Loss: Total premium paid
    """
    
    def __init__(self):
        super().__init__("Long Straddle", StrategyType.AGGRESSIVE)
        
        # Strategy specific parameters
        self.max_premium_paid = 150  # Maximum total premium for both legs
        self.max_loss_percentage = 0.03  # Max 3% of capital per trade (higher for aggressive)
        self.target_dte = 20  # Prefer options with some time but not too much decay
        self.min_iv_percentile = 15  # Needs low IV to buy cheap
        self.max_iv_percentile = 40  # Don't buy when IV is too high
        self.profit_target = 1.5  # Take profit at 150% of premium paid
        self.stop_loss = 0.5  # Stop loss at 50% of premium paid
        self.min_expected_move = 0.03  # Minimum 3% expected move to trigger
        
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        if not self._is_market_suitable_for_long_straddle(market_data):
            return []
        
        signals = []
        
        try:
            if "NIFTY" in market_data.symbol or "BANKNIFTY" in market_data.symbol:
                signal = await self._create_long_straddle_signal(market_data)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error generating Long Straddle signals: {e}")
            
        return signals
    
    async def _create_long_straddle_signal(self, market_data: MarketData) -> Optional[StrategySignal]:
        spot_price = market_data.spot_price
        underlying = market_data.symbol
        
        # Strike interval based on underlying
        strike_interval = 50 if underlying == "NIFTY" else 100
        
        # For straddle, use ATM strike (or closest to ATM)
        atm_strike = round(spot_price / strike_interval) * strike_interval
        
        # Create the two legs of Long Straddle (both ATM)
        legs = [
            # Buy ATM call
            OptionLeg(
                strike_price=atm_strike,
                option_type=OptionType.CALL,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(atm_strike, spot_price, OptionType.CALL, market_data.iv)
            ),
            # Buy ATM put
            OptionLeg(
                strike_price=atm_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(atm_strike, spot_price, OptionType.PUT, market_data.iv)
            )
        ]
        
        # Calculate total premium paid (debit)
        total_premium = legs[0].premium + legs[1].premium
        
        # Check if premium is within acceptable range
        if total_premium > self.max_premium_paid:
            return None
        
        # Calculate max profit and loss
        max_loss = total_premium
        max_profit = float('inf')  # Theoretically unlimited
        
        # Calculate breakeven points
        upper_breakeven = atm_strike + total_premium
        lower_breakeven = atm_strike - total_premium
        
        # Calculate expected move and probability of profit
        expected_move = self._calculate_expected_move(market_data, self.target_dte)
        
        # Probability of profit = probability of moving beyond breakevens
        prob_up = self._calculate_move_probability(spot_price, upper_breakeven, expected_move)
        prob_down = self._calculate_move_probability(spot_price, lower_breakeven, -expected_move)
        probability_of_profit = prob_up + prob_down
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            market_data, total_premium, probability_of_profit, expected_move
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
            breakeven_points=[lower_breakeven, upper_breakeven],
            probability_of_profit=probability_of_profit,
            confidence_score=confidence_score,
            expiry_date=expiry_date
        )
        
        return signal
    
    def _is_market_suitable_for_long_straddle(self, market_data: MarketData) -> bool:
        # Skip market hours check for testing
        
        # Check IV levels (need low to medium IV to buy straddles)
        if market_data.iv < self.min_iv_percentile or market_data.iv > self.max_iv_percentile:
            return False
        
        # Check volume
        if market_data.volume < 200000:  # Higher volume needed for straddles
            return False
        
        # Check if we expect sufficient movement
        expected_move = self._calculate_expected_move(market_data, self.target_dte)
        if expected_move < self.min_expected_move:
            return False
        
        return True
    
    def _calculate_expected_move(self, market_data: MarketData, days: int) -> float:
        # Simple expected move calculation using IV
        # Expected move = Spot * IV * sqrt(days/365)
        return market_data.spot_price * (market_data.iv / 100) * math.sqrt(days / 365)
    
    def _calculate_move_probability(self, spot: float, target: float, expected_move: float) -> float:
        # Simplified probability calculation
        # Higher probability if target is within expected move
        distance = abs(target - spot)
        if expected_move <= 0:
            return 0.1
        
        prob = max(0.1, 0.4 * (expected_move / distance))
        return min(prob, 0.45)  # Cap at 45% for each direction
    
    def _estimate_premium(self, strike: float, spot: float, option_type: OptionType, iv: float) -> float:
        # ATM options have high time value
        points_from_atm = abs(strike - spot)
        
        base_time_value = iv * 0.4 * math.sqrt(self.target_dte/365)  # Higher multiplier for straddles
        
        # Intrinsic value
        if option_type == OptionType.CALL:
            intrinsic = max(0, spot - strike)
        else:  # PUT  
            intrinsic = max(0, strike - spot)
        
        # ATM options have maximum time value
        if points_from_atm <= 50:  # Very close to ATM
            time_value = base_time_value * 120
        elif points_from_atm <= 100:  # Near ATM
            time_value = base_time_value * 100
        else:  # Away from ATM
            time_value = base_time_value * 60
        
        premium = intrinsic + time_value
        
        # Higher minimum premium for ATM options
        premium = max(premium, 25.0 if points_from_atm <= 100 else 15.0)
        
        return round(premium, 2)
    
    def _calculate_confidence_score(self, market_data: MarketData, total_premium: float, 
                                  pop: float, expected_move: float) -> float:
        score = 0.0
        
        # IV component (25% weight) - lower IV is better for buying
        iv_score = max(0.2, 1.0 - (market_data.iv / 50))
        score += iv_score * 0.25
        
        # Cost efficiency component (25% weight) - lower cost is better
        cost_score = max(0.2, 1.0 - (total_premium / self.max_premium_paid))
        score += cost_score * 0.25
        
        # Probability of profit component (25% weight)
        score += pop * 0.25
        
        # Expected move component (25% weight) - higher expected move is better
        move_score = min(expected_move / (market_data.spot_price * 0.05), 1.0)
        score += move_score * 0.25
        
        return min(score, 0.90)  # Cap slightly lower for aggressive strategies
    
    def validate_signal(self, signal: StrategySignal, current_positions: int) -> bool:
        # Check position limits (lower for aggressive strategies)
        if current_positions >= min(self.max_positions, 3):
            return False
        
        # Check confidence threshold
        if signal.confidence_score < self.min_confidence:
            return False
        
        # Check max loss vs capital (total premium paid)
        if signal.max_loss > (self.max_loss_percentage * 100000):
            return False
        
        # Validate Long Straddle structure (2 legs, same strike, one call one put)
        if len(signal.legs) != 2:
            return False
        
        calls = [leg for leg in signal.legs if leg.option_type == OptionType.CALL]
        puts = [leg for leg in signal.legs if leg.option_type == OptionType.PUT]
        
        if len(calls) != 1 or len(puts) != 1:
            return False
        
        # Check that both legs are BUY orders
        buys = [leg for leg in signal.legs if leg.order_type == OrderType.BUY]
        if len(buys) != 2:
            return False
        
        # Check that both legs have same strike (ATM straddle)
        if signal.legs[0].strike_price != signal.legs[1].strike_price:
            return False
        
        return True
    
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        # More conservative position sizing for aggressive strategies
        max_risk_per_trade = available_capital * self.max_loss_percentage
        
        # Calculate lots based on max loss per lot (total premium)
        max_loss_per_lot = signal.max_loss
        max_lots = int(max_risk_per_trade / max_loss_per_lot) if max_loss_per_lot > 0 else 1
        
        # Very conservative sizing for volatility strategies
        return min(max_lots, 2) if max_lots > 0 else 1