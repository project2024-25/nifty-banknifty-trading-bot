from typing import List, Optional
from datetime import datetime, timedelta
import math

from ..base_strategy import (
    BaseStrategy, StrategySignal, MarketData, OptionLeg, 
    OptionType, OrderType, StrategyType
)


class LongStrangleStrategy(BaseStrategy):
    """
    Long Strangle Strategy (Aggressive)
    
    Volatility strategy expecting large price movement in either direction.
    Structure: Buy OTM call + Buy OTM put (cheaper than straddle)
    
    Market View: Expects high volatility (direction agnostic) but lower cost than straddle
    Max Profit: Unlimited (theoretically)
    Max Loss: Total premium paid
    """
    
    def __init__(self):
        super().__init__("Long Strangle", StrategyType.AGGRESSIVE)
        
        # Strategy specific parameters
        self.max_premium_paid = 100  # Maximum total premium (cheaper than straddle)
        self.max_loss_percentage = 0.025  # Max 2.5% of capital per trade
        self.target_dte = 25  # Prefer options with some time
        self.min_iv_percentile = 15  # Needs low IV to buy cheap
        self.max_iv_percentile = 35  # Don't buy when IV is too high
        self.profit_target = 2.0  # Take profit at 200% of premium paid
        self.stop_loss = 0.4  # Stop loss at 40% of premium paid
        self.min_expected_move = 0.04  # Minimum 4% expected move (higher than straddle)
        self.otm_distance = 0.02  # 2% OTM for both calls and puts
        
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        if not self._is_market_suitable_for_long_strangle(market_data):
            return []
        
        signals = []
        
        try:
            if "NIFTY" in market_data.symbol or "BANKNIFTY" in market_data.symbol:
                signal = await self._create_long_strangle_signal(market_data)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error generating Long Strangle signals: {e}")
            
        return signals
    
    async def _create_long_strangle_signal(self, market_data: MarketData) -> Optional[StrategySignal]:
        spot_price = market_data.spot_price
        underlying = market_data.symbol
        
        # Strike interval based on underlying
        strike_interval = 50 if underlying == "NIFTY" else 100
        
        # Calculate OTM strikes for strangle
        otm_distance_points = spot_price * self.otm_distance
        
        # Call strike - OTM above current price
        call_strike = spot_price + otm_distance_points
        call_strike = round(call_strike / strike_interval) * strike_interval
        
        # Put strike - OTM below current price
        put_strike = spot_price - otm_distance_points
        put_strike = round(put_strike / strike_interval) * strike_interval
        
        # Create the two legs of Long Strangle
        legs = [
            # Buy OTM call
            OptionLeg(
                strike_price=call_strike,
                option_type=OptionType.CALL,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(call_strike, spot_price, OptionType.CALL, market_data.iv)
            ),
            # Buy OTM put
            OptionLeg(
                strike_price=put_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(put_strike, spot_price, OptionType.PUT, market_data.iv)
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
        upper_breakeven = call_strike + total_premium
        lower_breakeven = put_strike - total_premium
        
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
    
    def _is_market_suitable_for_long_strangle(self, market_data: MarketData) -> bool:
        # Skip market hours check for testing
        
        # Check IV levels (need low to medium IV to buy strangles)
        if market_data.iv < self.min_iv_percentile or market_data.iv > self.max_iv_percentile:
            return False
        
        # Check volume
        if market_data.volume < 150000:
            return False
        
        # Check if we expect sufficient movement (higher than straddle due to OTM strikes)
        expected_move = self._calculate_expected_move(market_data, self.target_dte)
        if expected_move < self.min_expected_move:
            return False
        
        return True
    
    def _calculate_expected_move(self, market_data: MarketData, days: int) -> float:
        # Expected move calculation using IV
        return market_data.spot_price * (market_data.iv / 100) * math.sqrt(days / 365)
    
    def _calculate_move_probability(self, spot: float, target: float, expected_move: float) -> float:
        # Probability calculation for reaching breakeven
        distance = abs(target - spot)
        if expected_move <= 0:
            return 0.1
        
        prob = max(0.1, 0.35 * (expected_move / distance))  # Slightly lower than straddle
        return min(prob, 0.4)  # Cap at 40% for each direction
    
    def _estimate_premium(self, strike: float, spot: float, option_type: OptionType, iv: float) -> float:
        # OTM options have lower premiums than ATM
        points_from_atm = abs(strike - spot)
        
        base_time_value = iv * 0.35 * math.sqrt(self.target_dte/365)
        
        # Intrinsic value (should be 0 for OTM options)
        if option_type == OptionType.CALL:
            intrinsic = max(0, spot - strike)
        else:  # PUT  
            intrinsic = max(0, strike - spot)
        
        # Time value for OTM options
        if points_from_atm <= 100:  # Near ATM
            time_value = base_time_value * 80
        elif points_from_atm <= 200:  # Moderately OTM
            time_value = base_time_value * 60
        else:  # Far OTM
            time_value = base_time_value * 40
        
        premium = intrinsic + time_value
        
        # Minimum premium for OTM options
        premium = max(premium, 18.0 if points_from_atm <= 150 else 10.0)
        
        return round(premium, 2)
    
    def _calculate_confidence_score(self, market_data: MarketData, total_premium: float, 
                                  pop: float, expected_move: float) -> float:
        score = 0.0
        
        # IV component (25% weight) - lower IV is better for buying
        iv_score = max(0.2, 1.0 - (market_data.iv / 45))
        score += iv_score * 0.25
        
        # Cost efficiency component (25% weight) - lower cost is better
        cost_score = max(0.2, 1.0 - (total_premium / self.max_premium_paid))
        score += cost_score * 0.25
        
        # Probability of profit component (25% weight)
        score += pop * 0.25
        
        # Expected move component (25% weight) - higher expected move is better
        move_score = min(expected_move / (market_data.spot_price * 0.06), 1.0)
        score += move_score * 0.25
        
        return min(score, 0.88)  # Cap for aggressive strategies
    
    def validate_signal(self, signal: StrategySignal, current_positions: int) -> bool:
        # Check position limits
        if current_positions >= min(self.max_positions, 3):
            return False
        
        # Check confidence threshold
        if signal.confidence_score < self.min_confidence:
            return False
        
        # Check max loss vs capital
        if signal.max_loss > (self.max_loss_percentage * 100000):
            return False
        
        # Validate Long Strangle structure (2 legs, different strikes, one call one put)
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
        
        # Check that strikes are different (strangle, not straddle)
        if signal.legs[0].strike_price == signal.legs[1].strike_price:
            return False
        
        return True
    
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        # Conservative position sizing for aggressive strategies
        max_risk_per_trade = available_capital * self.max_loss_percentage
        
        # Calculate lots based on max loss per lot (total premium)
        max_loss_per_lot = signal.max_loss
        max_lots = int(max_risk_per_trade / max_loss_per_lot) if max_loss_per_lot > 0 else 1
        
        # Conservative sizing for volatility strategies
        return min(max_lots, 2) if max_lots > 0 else 1