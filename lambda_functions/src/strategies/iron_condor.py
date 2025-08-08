from typing import List, Optional
from datetime import datetime, timedelta
import math

from .base_strategy import (
    BaseStrategy, StrategySignal, MarketData, OptionLeg, 
    OptionType, OrderType, StrategyType
)


class IronCondorStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Iron Condor", StrategyType.CONSERVATIVE)
        
        # Iron Condor specific parameters
        self.wing_width = 100  # Points between strikes
        self.min_premium_collected = 10  # Minimum premium to collect (reduced for testing)
        self.max_loss_percentage = 0.02  # Max 2% of capital per trade
        self.target_dte = 30  # Days to expiration
        self.iv_percentile_min = 30  # Minimum IV percentile
        self.profit_target = 0.5  # Take profit at 50% of max profit
        self.stop_loss = 2.0  # Stop loss at 200% of premium collected
        
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        if not self._is_market_suitable_for_iron_condor(market_data):
            return []
        
        signals = []
        
        try:
            # Generate NIFTY Iron Condor
            if "NIFTY" in market_data.symbol:
                nifty_signal = await self._create_iron_condor_signal(market_data, "NIFTY")
                if nifty_signal:
                    signals.append(nifty_signal)
            
            # Generate BANKNIFTY Iron Condor
            if "BANKNIFTY" in market_data.symbol:
                banknifty_signal = await self._create_iron_condor_signal(market_data, "BANKNIFTY")
                if banknifty_signal:
                    signals.append(banknifty_signal)
                    
        except Exception as e:
            print(f"Error generating Iron Condor signals: {e}")
            
        return signals
    
    async def _create_iron_condor_signal(self, market_data: MarketData, underlying: str) -> Optional[StrategySignal]:
        spot_price = market_data.spot_price
        
        # Calculate strike prices for Iron Condor
        # Structure: Sell Put, Buy Put (lower), Sell Call, Buy Call (higher)
        
        # For NIFTY: strikes are typically in multiples of 50
        # For BANKNIFTY: strikes are typically in multiples of 100
        strike_interval = 50 if underlying == "NIFTY" else 100
        
        # Round spot price to nearest strike interval
        atm_strike = round(spot_price / strike_interval) * strike_interval
        
        # Define the Iron Condor strikes
        # Short put strike (below ATM)
        short_put_strike = atm_strike - (2 * strike_interval)
        # Long put strike (further below)
        long_put_strike = short_put_strike - self.wing_width
        
        # Short call strike (above ATM) 
        short_call_strike = atm_strike + (2 * strike_interval)
        # Long call strike (further above)
        long_call_strike = short_call_strike + self.wing_width
        
        # Create the four legs of Iron Condor
        legs = [
            # Put spread (sell high strike put, buy low strike put)
            OptionLeg(
                strike_price=short_put_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.SELL,
                quantity=1,
                premium=self._estimate_premium(short_put_strike, spot_price, OptionType.PUT, market_data.iv)
            ),
            OptionLeg(
                strike_price=long_put_strike, 
                option_type=OptionType.PUT,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(long_put_strike, spot_price, OptionType.PUT, market_data.iv)
            ),
            # Call spread (sell low strike call, buy high strike call)
            OptionLeg(
                strike_price=short_call_strike,
                option_type=OptionType.CALL,
                order_type=OrderType.SELL,
                quantity=1,
                premium=self._estimate_premium(short_call_strike, spot_price, OptionType.CALL, market_data.iv)
            ),
            OptionLeg(
                strike_price=long_call_strike,
                option_type=OptionType.CALL,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(long_call_strike, spot_price, OptionType.CALL, market_data.iv)
            )
        ]
        
        # Calculate net premium collected (credit received)
        net_premium = sum(
            leg.premium * (1 if leg.order_type == OrderType.SELL else -1) 
            for leg in legs
        )
        
        # Check if premium meets minimum requirement
        if net_premium < self.min_premium_collected:
            return None
        
        # Calculate max profit and loss
        max_profit = net_premium
        max_loss = self.wing_width - net_premium
        
        # Calculate breakeven points
        lower_breakeven = short_put_strike - net_premium
        upper_breakeven = short_call_strike + net_premium
        
        # Calculate probability of profit (simplified)
        profit_range = upper_breakeven - lower_breakeven
        total_range = long_call_strike - long_put_strike
        probability_of_profit = (profit_range / total_range) * 0.85  # Conservative estimate
        
        # Calculate confidence score based on multiple factors
        confidence_score = self._calculate_confidence_score(
            market_data, net_premium, probability_of_profit
        )
        
        if confidence_score < self.min_confidence:
            return None
        
        # Create expiry date (typically weekly options)
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
    
    def _is_market_suitable_for_iron_condor(self, market_data: MarketData) -> bool:
        # For testing, skip market hours check
        # if not self._is_market_suitable(market_data):
        #     return False
        
        # Check IV levels (Iron Condor works best in high IV environments)
        if market_data.iv < self.iv_percentile_min:
            return False
        
        # Check volume and open interest
        if market_data.volume < 100000:  # Minimum volume threshold
            return False
            
        return True
    
    def _estimate_premium(self, strike: float, spot: float, option_type: OptionType, iv: float) -> float:
        # Realistic premium estimation for Indian options
        # Based on typical NIFTY/BANKNIFTY option premiums
        
        # Distance from ATM
        points_from_atm = abs(strike - spot)
        
        # Base time value (scaled for Indian markets)
        base_time_value = iv * 0.3 * math.sqrt(30/365)  # Higher base for Indian volatility
        
        # Intrinsic value
        if option_type == OptionType.CALL:
            intrinsic = max(0, spot - strike)
        else:  # PUT  
            intrinsic = max(0, strike - spot)
        
        # Time value decreases with distance from ATM
        if points_from_atm <= 100:  # ATM/Near ATM
            time_value = base_time_value * 80
        elif points_from_atm <= 200:  # Slightly OTM
            time_value = base_time_value * 50
        else:  # Far OTM
            time_value = base_time_value * 25
        
        premium = intrinsic + time_value
        
        # Minimum premium (typical for Indian options)
        premium = max(premium, 15.0 if points_from_atm <= 200 else 8.0)
        
        return round(premium, 2)
    
    def _calculate_confidence_score(self, market_data: MarketData, net_premium: float, pop: float) -> float:
        score = 0.0
        
        # IV component (30% weight)
        iv_score = min(market_data.iv / 50, 1.0)  # Normalize to 50% IV
        score += iv_score * 0.3
        
        # Premium component (25% weight)  
        premium_score = min(net_premium / 100, 1.0)  # Normalize to 100 premium
        score += premium_score * 0.25
        
        # Probability of profit component (25% weight)
        score += pop * 0.25
        
        # Volume/liquidity component (20% weight)
        volume_score = min(market_data.volume / 500000, 1.0)  # Normalize to 500k volume
        score += volume_score * 0.2
        
        return min(score, 0.95)  # Cap at 95% confidence
    
    def validate_signal(self, signal: StrategySignal, current_positions: int) -> bool:
        # Check position limits
        if current_positions >= self.max_positions:
            return False
        
        # Check confidence threshold
        if signal.confidence_score < self.min_confidence:
            return False
        
        # Check max loss vs capital
        if signal.max_loss > (self.max_loss_percentage * 100000):  # Assuming 1L capital
            return False
        
        # Validate Iron Condor structure
        if len(signal.legs) != 4:
            return False
        
        # Check that we have both puts and calls
        puts = [leg for leg in signal.legs if leg.option_type == OptionType.PUT]
        calls = [leg for leg in signal.legs if leg.option_type == OptionType.CALL]
        
        if len(puts) != 2 or len(calls) != 2:
            return False
        
        return True
    
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        # Conservative position sizing for Iron Condor
        max_risk_per_trade = available_capital * self.max_loss_percentage
        
        # Calculate lots based on max loss per lot (use absolute value)
        max_loss_per_lot = abs(signal.max_loss)
        max_lots = int(max_risk_per_trade / max_loss_per_lot) if max_loss_per_lot > 0 else 1
        
        # Conservative sizing: start with 1 lot for Iron Condors
        # Can be increased based on performance
        return min(max_lots, 1) if max_lots > 0 else 1