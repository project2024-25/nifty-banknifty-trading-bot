from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime


class OptionType(Enum):
    CALL = "CE"
    PUT = "PE"


class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class StrategyType(Enum):
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"


@dataclass
class OptionLeg:
    strike_price: float
    option_type: OptionType
    order_type: OrderType
    quantity: int
    premium: Optional[float] = None
    symbol: Optional[str] = None


@dataclass
class StrategySignal:
    strategy_name: str
    symbol: str
    legs: List[OptionLeg]
    max_profit: float
    max_loss: float
    breakeven_points: List[float]
    probability_of_profit: Optional[float] = None
    confidence_score: float = 0.0
    expiry_date: Optional[datetime] = None
    generated_at: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()


@dataclass
class MarketData:
    symbol: str
    spot_price: float
    iv: float
    volume: int
    oi: int
    last_updated: datetime


class BaseStrategy(ABC):
    def __init__(self, name: str, strategy_type: StrategyType):
        self.name = name
        self.strategy_type = strategy_type
        self.is_active = True
        self.max_positions = 5
        self.min_confidence = 0.6
        
    @abstractmethod
    async def generate_signals(self, market_data: MarketData) -> List[StrategySignal]:
        pass
    
    @abstractmethod
    def validate_signal(self, signal: StrategySignal, current_positions: int) -> bool:
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: StrategySignal, available_capital: float) -> int:
        pass
    
    def get_strategy_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.strategy_type.value,
            "active": self.is_active,
            "max_positions": self.max_positions,
            "min_confidence": self.min_confidence
        }
    
    def _is_market_suitable(self, market_data: MarketData) -> bool:
        current_time = datetime.now().time()
        market_open = datetime.strptime("09:15", "%H:%M").time()
        market_close = datetime.strptime("15:30", "%H:%M").time()
        
        return market_open <= current_time <= market_close
    
    def _calculate_greeks_impact(self, legs: List[OptionLeg], spot_price: float) -> Dict[str, float]:
        total_delta = 0.0
        total_gamma = 0.0
        total_theta = 0.0
        total_vega = 0.0
        
        for leg in legs:
            multiplier = 1 if leg.order_type == OrderType.BUY else -1
            
            if leg.option_type == OptionType.CALL:
                if leg.strike_price < spot_price:
                    delta = 0.6 * multiplier
                else:
                    delta = 0.3 * multiplier
            else:
                if leg.strike_price > spot_price:
                    delta = -0.6 * multiplier
                else:
                    delta = -0.3 * multiplier
            
            total_delta += delta * leg.quantity
            total_gamma += 0.1 * multiplier * leg.quantity
            total_theta += -0.05 * multiplier * leg.quantity
            total_vega += 0.2 * multiplier * leg.quantity
        
        return {
            "delta": total_delta,
            "gamma": total_gamma,
            "theta": total_theta,
            "vega": total_vega
        }