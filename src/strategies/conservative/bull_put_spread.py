from typing import List, Optional
from datetime import datetime, timedelta
import math

from ..base_strategy import (
    BaseStrategy, StrategySignal, MarketData, OptionLeg, 
    OptionType, OrderType, StrategyType
)


class BullPutSpreadStrategy(BaseStrategy):
    """
    Bull Put Spread Strategy (Conservative)
    
    Bullish strategy with limited risk and limited profit.
    Structure: Sell higher strike put (collect premium), Buy lower strike put (protection)
    
    Market View: Mildly to moderately bullish
    Max Profit: Net premium collected
    Max Loss: (Strike difference - Net premium)
    """
    
    def __init__(self):
        super().__init__("Bull Put Spread", StrategyType.CONSERVATIVE)
        
        # Strategy specific parameters
        self.spread_width = 100  # Points between strikes
        self.min_premium_collected = 20  # Minimum net credit
        self.max_loss_percentage = 0.015  # Max 1.5% of capital per trade
        self.target_dte = 15  # Prefer weekly options (15 days)
        self.min_iv_percentile = 25  # Works in medium to high IV
        self.profit_target = 0.5  # Take profit at 50% of max profit
        self.stop_loss = 2.0  # Stop loss at 200% of premium collected
        self.min_moneyness = 0.02  # Minimum 2% OTM for short put
        
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        if not self._is_market_suitable_for_bull_put_spread(market_data):
            return []
        
        signals = []
        
        try:
            if "NIFTY" in market_data.symbol or "BANKNIFTY" in market_data.symbol:
                signal = await self._create_bull_put_spread_signal(market_data)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            print(f"Error generating Bull Put Spread signals: {e}")
            
        return signals
    
    async def _create_bull_put_spread_signal(self, market_data: MarketData) -> Optional[StrategySignal]:
        spot_price = market_data.spot_price
        underlying = market_data.symbol
        
        # Strike interval based on underlying
        strike_interval = 50 if underlying == "NIFTY" else 100
        
        # Calculate strikes for Bull Put Spread
        # We want to sell a put below current price (collect premium)
        # And buy a put further below (protection)
        
        # Short put strike (higher strike) - should be OTM
        atm_strike = round(spot_price / strike_interval) * strike_interval
        min_otm_distance = max(2 * strike_interval, spot_price * self.min_moneyness)
        short_put_strike = atm_strike - min_otm_distance
        
        # Long put strike (lower strike) - protection
        long_put_strike = short_put_strike - self.spread_width
        
        # Create the two legs of Bull Put Spread
        legs = [
            # Sell higher strike put (collect premium)
            OptionLeg(
                strike_price=short_put_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.SELL,
                quantity=1,
                premium=self._estimate_premium(short_put_strike, spot_price, OptionType.PUT, market_data.iv)
            ),
            # Buy lower strike put (pay premium for protection)
            OptionLeg(
                strike_price=long_put_strike,
                option_type=OptionType.PUT,
                order_type=OrderType.BUY,
                quantity=1,
                premium=self._estimate_premium(long_put_strike, spot_price, OptionType.PUT, market_data.iv)
            )
        ]
        
        # Calculate net premium (credit received)
        net_premium = legs[0].premium - legs[1].premium
        
        # Check if premium meets minimum requirement
        if net_premium < self.min_premium_collected:
            return None
        
        # Calculate max profit and loss
        max_profit = net_premium
        max_loss = self.spread_width - net_premium
        
        # Calculate breakeven point
        breakeven_point = short_put_strike - net_premium
        
        # Calculate probability of profit (simplified)
        # Profit if spot stays above breakeven
        distance_to_breakeven = spot_price - breakeven_point
        probability_of_profit = min(0.85, distance_to_breakeven / (spot_price * 0.1))
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            market_data, net_premium, probability_of_profit, distance_to_breakeven
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
    
    def _is_market_suitable_for_bull_put_spread(self, market_data: MarketData) -> bool:
        # Skip market hours check for testing
        
        # Check IV levels (works better in higher IV)
        if market_data.iv < self.min_iv_percentile:
            return False
        
        # Check volume
        if market_data.volume < 100000:
            return False
        
        # Bull Put Spread works when we expect price to stay above short strike
        # Better in uptrending or sideways markets
        return True
    
    def _estimate_premium(self, strike: float, spot: float, option_type: OptionType, iv: float) -> float:
        # Use the same premium estimation as Iron Condor for consistency
        points_from_atm = abs(strike - spot)
        
        base_time_value = iv * 0.3 * math.sqrt(self.target_dte/365)
        
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
        
        # Minimum premium
        premium = max(premium, 10.0 if points_from_atm <= 200 else 5.0)
        
        return round(premium, 2)
    
    def _calculate_confidence_score(self, market_data: MarketData, net_premium: float, 
                                  pop: float, distance_to_breakeven: float) -> float:
        score = 0.0
        
        # IV component (25% weight)
        iv_score = min(market_data.iv / 40, 1.0)
        score += iv_score * 0.25
        
        # Premium component (25% weight)  
        premium_score = min(net_premium / 50, 1.0)
        score += premium_score * 0.25
        
        # Probability of profit component (25% weight)
        score += max(pop, 0.3) * 0.25  # Min 30% for scoring
        
        # Distance to breakeven (25% weight) - further is better
        distance_score = min(distance_to_breakeven / (market_data.spot_price * 0.05), 1.0)
        score += distance_score * 0.25
        
        return min(score, 0.95)
    
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
        
        # Validate Bull Put Spread structure (2 legs, both puts)
        if len(signal.legs) != 2:
            return False
        
        puts = [leg for leg in signal.legs if leg.option_type == OptionType.PUT]
        if len(puts) != 2:
            return False
        
        # Check that we have one sell and one buy
        sells = [leg for leg in signal.legs if leg.order_type == OrderType.SELL]
        buys = [leg for leg in signal.legs if leg.order_type == OrderType.BUY]
        
        if len(sells) != 1 or len(buys) != 1:
            return False
        
        return True
    
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        # Conservative position sizing for Bull Put Spread
        max_risk_per_trade = available_capital * self.max_loss_percentage
        
        # Calculate lots based on max loss per lot
        max_loss_per_lot = abs(signal.max_loss)
        max_lots = int(max_risk_per_trade / max_loss_per_lot) if max_loss_per_lot > 0 else 1
        
        # Conservative sizing: start with 1-2 lots for spreads
        return min(max_lots, 2) if max_lots > 0 else 1