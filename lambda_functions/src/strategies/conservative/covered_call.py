from typing import List, Optional
from datetime import datetime, timedelta
import math

from ..base_strategy import (
    BaseStrategy, StrategySignal, MarketData, OptionLeg, 
    OptionType, OrderType, StrategyType
)


class CoveredCallStrategy(BaseStrategy):
    """
    Covered Call Strategy (Conservative)
    
    Income generation strategy for neutral to mildly bullish outlook.
    Structure: Long underlying stock/futures + Short call (simulated with cash secured put equivalent)
    
    Note: For options-only implementation, we'll use a synthetic equivalent or cash-secured put approach.
    
    Market View: Neutral to mildly bullish, expecting sideways to slight upward movement
    Max Profit: Premium collected + (Strike - Purchase price) if called away
    Max Loss: Significant if underlying drops substantially
    """
    
    def __init__(self):
        super().__init__("Covered Call", StrategyType.CONSERVATIVE)
        
        # Strategy specific parameters
        self.min_premium_collected = 25  # Minimum call premium to collect
        self.max_loss_percentage = 0.02  # Max 2% of capital per trade
        self.target_dte = 30  # Prefer monthly options for income
        self.min_iv_percentile = 25  # Need decent IV for premium collection
        self.profit_target = 0.8  # Take profit at 80% of max profit
        self.stop_loss = 1.5  # Stop loss at 150% of premium collected
        self.min_otm_distance = 0.02  # Minimum 2% OTM for call strike
        self.max_otm_distance = 0.05  # Maximum 5% OTM for call strike
        
        # Note: In a real implementation, this would require stock/futures positions
        # For options-only approach, we'll implement a synthetic equivalent
        
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        if not self._is_market_suitable_for_covered_call(market_data):
            return []
        
        signals = []
        
        try:
            if "NIFTY" in market_data.symbol or "BANKNIFTY" in market_data.symbol:
                signal = await self._create_covered_call_signal(market_data)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error generating Covered Call signals: {e}")
            
        return signals
    
    async def _create_covered_call_signal(self, market_data: MarketData) -> Optional[StrategySignal]:
        spot_price = market_data.spot_price
        underlying = market_data.symbol
        
        # Strike interval based on underlying
        strike_interval = 50 if underlying == "NIFTY" else 100
        
        # Calculate OTM call strike for covered call
        min_call_strike = spot_price * (1 + self.min_otm_distance)
        max_call_strike = spot_price * (1 + self.max_otm_distance)
        
        # Choose strike in the middle of the range
        target_call_strike = (min_call_strike + max_call_strike) / 2
        call_strike = round(target_call_strike / strike_interval) * strike_interval
        
        # For options-only implementation, we'll create a synthetic covered call
        # using a combination that mimics the risk profile
        # Synthetic approach: Sell OTM Call + Buy ATM Put (protective put equivalent)
        
        atm_strike = round(spot_price / strike_interval) * strike_interval
        
        # Create legs for synthetic covered call
        legs = [
            # Sell OTM call (income generation)
            OptionLeg(
                strike_price=call_strike,
                option_type=OptionType.CALL,
                order_type=OrderType.SELL,
                quantity=1,
                premium=self._estimate_premium(call_strike, spot_price, OptionType.CALL, market_data.iv)
            ),
            # Buy ATM put for protection (simulating stock ownership protection)
            OptionLeg(
                strike_price=atm_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(atm_strike, spot_price, OptionType.PUT, market_data.iv)
            )
        ]
        
        # Calculate net premium (call premium - put premium)
        net_premium = legs[0].premium - legs[1].premium
        
        # Check if we collect enough premium
        if net_premium < self.min_premium_collected:
            return None
        
        # Calculate max profit and loss for synthetic covered call
        max_profit = net_premium + (call_strike - atm_strike)  # Premium + upside to call strike
        max_loss = atm_strike - net_premium  # If stock goes to zero (worst case)
        
        # Calculate breakeven point
        breakeven_point = atm_strike + net_premium
        
        # Calculate probability of profit
        # Profit if stock stays above breakeven and below call strike
        probability_of_profit = self._calculate_covered_call_pop(
            spot_price, breakeven_point, call_strike, market_data
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            market_data, net_premium, probability_of_profit, call_strike - spot_price
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
    
    def _is_market_suitable_for_covered_call(self, market_data: MarketData) -> bool:
        # Skip market hours check for testing
        
        # Check IV levels (need decent IV for call premium)
        if market_data.iv < self.min_iv_percentile:
            return False
        
        # Check volume
        if market_data.volume < 100000:
            return False
        
        # Covered calls work best in neutral to mildly bullish markets
        return True
    
    def _calculate_covered_call_pop(self, spot: float, breakeven: float, 
                                   call_strike: float, market_data: MarketData) -> float:
        # Probability of profit for covered call (staying above breakeven, ideally below call strike)
        
        # Ideal profit zone: breakeven < price < call_strike
        ideal_range = call_strike - breakeven
        
        # Expected move
        expected_move = spot * (market_data.iv / 100) * math.sqrt(self.target_dte / 365)
        
        # Probability calculation
        if expected_move <= 0:
            return 0.65
        
        # Higher probability if ideal range is wider than expected move
        prob = min(0.8, 0.5 + (ideal_range / (expected_move * 1.5)))
        return max(prob, 0.4)
    
    def _estimate_premium(self, strike: float, spot: float, option_type: OptionType, iv: float) -> float:
        # Premium estimation for covered call legs
        points_from_atm = abs(strike - spot)
        
        base_time_value = iv * 0.35 * math.sqrt(self.target_dte/365)
        
        # Intrinsic value
        if option_type == OptionType.CALL:
            intrinsic = max(0, spot - strike)
        else:  # PUT  
            intrinsic = max(0, strike - spot)
        
        # Time value based on distance from ATM
        if points_from_atm <= 100:  # Near ATM
            time_value = base_time_value * 90
        elif points_from_atm <= 200:  # Moderately OTM
            time_value = base_time_value * 65
        else:  # Far OTM
            time_value = base_time_value * 40
        
        premium = intrinsic + time_value
        
        # Minimum premium for covered call options
        premium = max(premium, 18.0 if points_from_atm <= 150 else 10.0)
        
        return round(premium, 2)
    
    def _calculate_confidence_score(self, market_data: MarketData, net_premium: float, 
                                  pop: float, otm_distance: float) -> float:
        score = 0.0
        
        # IV component (25% weight) - higher IV is better for premium collection
        iv_score = min(market_data.iv / 45, 1.0)
        score += iv_score * 0.25
        
        # Premium component (30% weight) - higher premium is better
        premium_score = min(net_premium / 50, 1.0)
        score += premium_score * 0.3
        
        # Probability of profit component (25% weight)
        score += pop * 0.25
        
        # OTM distance component (20% weight) - optimal distance for covered calls
        optimal_distance = market_data.spot_price * 0.03  # 3% OTM is often optimal
        distance_score = max(0.3, 1.0 - abs(otm_distance - optimal_distance) / optimal_distance)
        score += distance_score * 0.2
        
        return min(score, 0.90)
    
    def validate_signal(self, signal: StrategySignal, current_positions: int) -> bool:
        # Check position limits
        if current_positions >= self.max_positions:
            return False
        
        # Check confidence threshold
        if signal.confidence_score < self.min_confidence:
            return False
        
        # Check max loss vs capital (for synthetic covered call)
        if signal.max_loss > (self.max_loss_percentage * 100000):
            return False
        
        # Validate Covered Call structure (2 legs: short call + long put)
        if len(signal.legs) != 2:
            return False
        
        calls = [leg for leg in signal.legs if leg.option_type == OptionType.CALL]
        puts = [leg for leg in signal.legs if leg.option_type == OptionType.PUT]
        
        if len(calls) != 1 or len(puts) != 1:
            return False
        
        # Check that call is sold and put is bought
        call_leg = calls[0]
        put_leg = puts[0]
        
        if call_leg.order_type != OrderType.SELL or put_leg.order_type != OrderType.BUY:
            return False
        
        # Check that call strike is above put strike (OTM call, ATM/ITM put)
        if call_leg.strike_price <= put_leg.strike_price:
            return False
        
        return True
    
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        # Conservative position sizing for covered calls
        max_risk_per_trade = available_capital * self.max_loss_percentage
        
        # For synthetic covered call, risk is primarily the put premium paid (net debit)
        max_loss_per_lot = abs(signal.max_loss)
        max_lots = int(max_risk_per_trade / max_loss_per_lot) if max_loss_per_lot > 0 else 1
        
        # Conservative sizing for income strategies
        return min(max_lots, 3) if max_lots > 0 else 1