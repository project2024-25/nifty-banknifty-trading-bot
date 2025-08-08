from typing import List, Optional
from datetime import datetime, timedelta
import math

from ..base_strategy import (
    BaseStrategy, StrategySignal, MarketData, OptionLeg, 
    OptionType, OrderType, StrategyType
)


class ShortStrangleStrategy(BaseStrategy):
    """
    Short Strangle Strategy (Aggressive)
    
    Volatility strategy expecting low volatility with wider profit range than short straddle.
    Structure: Sell OTM call + Sell OTM put
    
    Market View: Expects low to moderate volatility, sideways movement
    Max Profit: Total premium collected
    Max Loss: Unlimited (theoretically)
    """
    
    def __init__(self):
        super().__init__("Short Strangle", StrategyType.AGGRESSIVE)
        
        # Strategy specific parameters
        self.min_premium_collected = 60  # Minimum total premium (lower than straddle)
        self.max_loss_percentage = 0.04  # Max 4% of capital per trade
        self.target_dte = 20  # Prefer shorter expiry for time decay
        self.min_iv_percentile = 35  # Need high IV to sell expensive
        self.profit_target = 0.6  # Take profit at 60% of max profit
        self.stop_loss = 1.8  # Stop loss at 180% of premium collected
        self.max_expected_move = 0.025  # Maximum 2.5% expected move
        self.otm_distance = 0.03  # 3% OTM for both calls and puts
        
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        if not self._is_market_suitable_for_short_strangle(market_data):
            return []
        
        signals = []
        
        try:
            if "NIFTY" in market_data.symbol or "BANKNIFTY" in market_data.symbol:
                signal = await self._create_short_strangle_signal(market_data)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error generating Short Strangle signals: {e}")
            
        return signals
    
    async def _create_short_strangle_signal(self, market_data: MarketData) -> Optional[StrategySignal]:
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
        
        # Create the two legs of Short Strangle
        legs = [
            # Sell OTM call
            OptionLeg(
                strike_price=call_strike,
                option_type=OptionType.CALL,
                order_type=OrderType.SELL,
                quantity=1,
                premium=self._estimate_premium(call_strike, spot_price, OptionType.CALL, market_data.iv)
            ),
            # Sell OTM put
            OptionLeg(
                strike_price=put_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.SELL,
                quantity=1,
                premium=self._estimate_premium(put_strike, spot_price, OptionType.PUT, market_data.iv)
            )
        ]
        
        # Calculate total premium collected (credit)
        total_premium = legs[0].premium + legs[1].premium
        
        # Check if premium meets minimum requirement
        if total_premium < self.min_premium_collected:
            return None
        
        # Calculate max profit and loss
        max_profit = total_premium
        max_loss = float('inf')  # Theoretically unlimited
        
        # Calculate breakeven points
        upper_breakeven = call_strike + total_premium
        lower_breakeven = put_strike - total_premium
        
        # Calculate expected move and probability of profit
        expected_move = self._calculate_expected_move(market_data, self.target_dte)
        
        # Probability of profit = probability of staying between breakevens
        probability_of_profit = self._calculate_sideways_probability(
            spot_price, lower_breakeven, upper_breakeven, expected_move
        )
        
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
    
    def _is_market_suitable_for_short_strangle(self, market_data: MarketData) -> bool:
        # Skip market hours check for testing
        
        # Check IV levels (need high IV to sell strangles profitably)
        if market_data.iv < self.min_iv_percentile:
            return False
        
        # Check volume
        if market_data.volume < 150000:
            return False
        
        # Check if we expect low to moderate movement
        expected_move = self._calculate_expected_move(market_data, self.target_dte)
        if expected_move > self.max_expected_move:
            return False
        
        return True
    
    def _calculate_expected_move(self, market_data: MarketData, days: int) -> float:
        # Expected move calculation using IV
        return market_data.spot_price * (market_data.iv / 100) * math.sqrt(days / 365)
    
    def _calculate_sideways_probability(self, spot: float, lower_be: float, 
                                      upper_be: float, expected_move: float) -> float:
        # Probability that price stays between breakevens (wider than straddle)
        range_width = upper_be - lower_be
        
        if expected_move <= 0:
            return 0.75  # Default higher probability due to wider range
        
        # Higher probability due to wider breakeven range
        prob = min(0.88, 0.6 + (range_width / (expected_move * 2)))
        return max(prob, 0.5)  # Minimum 50% probability
    
    def _estimate_premium(self, strike: float, spot: float, option_type: OptionType, iv: float) -> float:
        # OTM options premiums for selling
        points_from_atm = abs(strike - spot)
        
        base_time_value = iv * 0.35 * math.sqrt(self.target_dte/365)
        
        # Intrinsic value (should be 0 for OTM options)
        if option_type == OptionType.CALL:
            intrinsic = max(0, spot - strike)
        else:  # PUT  
            intrinsic = max(0, strike - spot)
        
        # Time value for OTM options when selling
        if points_from_atm <= 100:  # Near ATM
            time_value = base_time_value * 85
        elif points_from_atm <= 200:  # Moderately OTM
            time_value = base_time_value * 65
        else:  # Far OTM
            time_value = base_time_value * 45
        
        premium = intrinsic + time_value
        
        # Higher minimum premium for selling OTM options
        premium = max(premium, 22.0 if points_from_atm <= 150 else 15.0)
        
        return round(premium, 2)
    
    def _calculate_confidence_score(self, market_data: MarketData, total_premium: float, 
                                  pop: float, expected_move: float) -> float:
        score = 0.0
        
        # IV component (30% weight) - higher IV is better for selling
        iv_score = min(market_data.iv / 55, 1.0)
        score += iv_score * 0.3
        
        # Premium component (25% weight) - higher premium is better
        premium_score = min(total_premium / 100, 1.0)
        score += premium_score * 0.25
        
        # Probability of profit component (30% weight)
        score += pop * 0.3
        
        # Low movement expectation (15% weight) - lower expected move is better
        move_score = max(0.2, 1.0 - (expected_move / (market_data.spot_price * 0.04)))
        score += move_score * 0.15
        
        return min(score, 0.83)  # Cap for unlimited risk strategies
    
    def validate_signal(self, signal: StrategySignal, current_positions: int) -> bool:
        # Very strict position limits for unlimited risk strategies
        if current_positions >= min(self.max_positions, 2):
            return False
        
        # Higher confidence threshold for risky strategies
        if signal.confidence_score < max(self.min_confidence, 0.65):
            return False
        
        # Validate Short Strangle structure (2 legs, different strikes, one call one put)
        if len(signal.legs) != 2:
            return False
        
        calls = [leg for leg in signal.legs if leg.option_type == OptionType.CALL]
        puts = [leg for leg in signal.legs if leg.option_type == OptionType.PUT]
        
        if len(calls) != 1 or len(puts) != 1:
            return False
        
        # Check that both legs are SELL orders
        sells = [leg for leg in signal.legs if leg.order_type == OrderType.SELL]
        if len(sells) != 2:
            return False
        
        # Check that strikes are different (strangle, not straddle)
        if signal.legs[0].strike_price == signal.legs[1].strike_price:
            return False
        
        return True
    
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        # Very conservative position sizing for unlimited risk strategies
        max_risk_per_trade = available_capital * self.max_loss_percentage
        
        # For unlimited risk strategies, base sizing on margin requirement
        # Estimate margin as 18% of underlying value per lot (slightly lower than straddle)
        estimated_margin_per_lot = (signal.legs[0].strike_price + signal.legs[1].strike_price) / 2 * 0.18
        max_lots = int(max_risk_per_trade / estimated_margin_per_lot) if estimated_margin_per_lot > 0 else 1
        
        # Very conservative sizing - only 1 lot for unlimited risk
        return min(max_lots, 1) if max_lots > 0 else 1