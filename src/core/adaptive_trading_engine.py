"""
Adaptive Trading Engine with Market Regime Intelligence
Enhanced trading engine that uses market regime detection for intelligent strategy selection
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from dataclasses import asdict

from src.utils.logger import get_logger
from src.utils.constants import RISK_LIMITS
from src.strategies.strategy_manager import StrategyManager
from src.strategies.base_strategy import MarketData
from src.intelligence.dashboard_simple import SimpleMarketDashboard, DashboardMetrics
from src.intelligence.strategy_selector import AdaptiveStrategySelector
from src.intelligence.dynamic_allocator import DynamicAllocationManager, AllocationMode
from src.intelligence.market_regime import MarketRegimeDetector


logger = get_logger(__name__)


class AdaptiveTradingEngine:
    """
    Enhanced trading engine with market regime intelligence.
    Replaces traditional fixed strategy approach with adaptive selection.
    """
    
    def __init__(self, initial_capital: float = 1000000):
        self.active = True
        self.paper_trading = True
        self.positions = {}
        self.daily_pnl = 0.0
        self.initial_capital = initial_capital
        
        # Intelligence components
        self.dashboard = SimpleMarketDashboard(capital=initial_capital)
        self.strategy_selector = AdaptiveStrategySelector()
        self.allocation_manager = DynamicAllocationManager(total_capital=initial_capital)
        self.regime_detector = MarketRegimeDetector()
        
        # Traditional components (for fallback)
        self.strategy_manager = None
        self.risk_manager = None
        self.broker = None
        
        # Engine configuration
        self.config = {
            'min_confidence_threshold': 0.6,
            'max_loss_per_trade': 10000,
            'allocation_mode': AllocationMode.REGIME_ADAPTIVE,
            'enable_regime_intelligence': True,
            'fallback_to_traditional': True,
            'update_dashboard_every_cycle': True
        }
        
        logger.info(
            "Adaptive Trading Engine initialized", 
            paper_trading=self.paper_trading,
            initial_capital=initial_capital,
            regime_intelligence=self.config['enable_regime_intelligence']
        )
    
    async def initialize(self):
        """Initialize adaptive trading engine components"""
        try:
            # Initialize traditional components first
            await self._initialize_broker()
            await self._initialize_risk_manager()
            
            # Initialize strategy manager for fallback
            if self.config['fallback_to_traditional']:
                await self._initialize_traditional_strategies()
            
            logger.info("Adaptive trading engine initialization completed")
            
        except Exception as e:
            logger.error(f"Adaptive trading engine initialization failed: {e}")
            raise
    
    async def execute_adaptive_trading_cycle(self) -> Dict[str, Any]:
        """Execute one complete adaptive trading cycle with regime intelligence"""
        try:
            logger.info("Starting adaptive trading cycle")
            
            # Check if trading is active
            if not self.active:
                return {"status": "Trading paused"}
            
            # Check market hours
            if not self._is_market_open():
                return {"status": "Market closed"}
            
            # Fetch market data
            market_data = await self._fetch_market_data()
            
            # Execute regime-based trading logic
            if self.config['enable_regime_intelligence']:
                result = await self._execute_regime_based_cycle(market_data)
            else:
                # Fallback to traditional approach
                result = await self._execute_traditional_cycle(market_data)
            
            # Update dashboard if enabled
            if self.config['update_dashboard_every_cycle']:
                await self._update_dashboard(market_data)
            
            logger.info("Adaptive trading cycle completed", result=result)
            return result
            
        except Exception as e:
            logger.error(f"Adaptive trading cycle failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _execute_regime_based_cycle(self, market_data: Dict[str, MarketData]) -> Dict[str, Any]:
        """Execute trading cycle using regime-based intelligence"""
        
        cycle_results = {
            "status": "success",
            "mode": "regime_adaptive",
            "symbols_processed": 0,
            "regimes_detected": {},
            "strategies_selected": {},
            "signals_generated": 0,
            "trades_executed": 0,
            "total_capital_deployed": 0.0,
            "risk_utilization": 0.0
        }
        
        for symbol, data in market_data.items():
            try:
                logger.info(f"Processing {symbol} with regime intelligence")
                
                # Step 1: Detect market regime for this symbol
                market_conditions = self.regime_detector.detect_regime(data)
                cycle_results["regimes_detected"][symbol] = market_conditions.regime.value
                
                logger.info(
                    f"Market regime detected for {symbol}",
                    regime=market_conditions.regime.value,
                    volatility=market_conditions.volatility_regime.value,
                    confidence=market_conditions.confidence_score
                )
                
                # Step 2: Select optimal strategies for this regime
                strategy_allocations = await self.strategy_selector.select_strategies(data)
                cycle_results["strategies_selected"][symbol] = len(strategy_allocations)
                
                if not strategy_allocations:
                    logger.info(f"No strategies selected for {symbol} in current regime")
                    continue
                
                # Step 3: Generate adaptive signals
                signals = await self.strategy_selector.generate_adaptive_signals(data)
                cycle_results["signals_generated"] += len(signals)
                
                if not signals:
                    logger.info(f"No signals generated for {symbol}")
                    continue
                
                # Step 4: Create portfolio allocation
                portfolio_allocation = self.allocation_manager.allocate_portfolio(
                    signals, market_conditions, self.config['allocation_mode']
                )
                
                # Step 5: Execute trades based on allocation
                executed_trades = await self._execute_allocated_trades(
                    portfolio_allocation, symbol
                )
                cycle_results["trades_executed"] += len(executed_trades)
                cycle_results["total_capital_deployed"] += portfolio_allocation.total_capital_used
                cycle_results["risk_utilization"] += portfolio_allocation.total_risk_allocated
                
                cycle_results["symbols_processed"] += 1
                
                logger.info(
                    f"Regime-based processing completed for {symbol}",
                    regime=market_conditions.regime.value,
                    strategies_selected=len(strategy_allocations),
                    signals=len(signals),
                    trades=len(executed_trades)
                )
                
            except Exception as e:
                logger.error(f"Regime processing failed for {symbol}: {e}")
                continue
        
        return cycle_results
    
    async def _execute_allocated_trades(self, allocation: Any, symbol: str) -> List[Dict[str, Any]]:
        """Execute trades based on portfolio allocation"""
        executed_trades = []
        
        for position in allocation.positions:
            try:
                # Enhanced validation with regime context
                if self._validate_regime_signal(position.signal, position):
                    if self.paper_trading:
                        trade = await self._execute_adaptive_paper_trade(position, symbol)
                    else:
                        trade = await self._execute_adaptive_live_trade(position, symbol)
                    
                    if trade:
                        executed_trades.append(trade)
                        logger.info(
                            "Adaptive trade executed",
                            trade_id=trade.get('id'),
                            strategy=trade.get('strategy'),
                            position_size=position.position_size
                        )
                        
            except Exception as e:
                logger.error(f"Adaptive trade execution failed: {e}")
        
        return executed_trades
    
    async def _execute_traditional_cycle(self, market_data: Dict[str, MarketData]) -> Dict[str, Any]:
        """Fallback to traditional trading cycle"""
        logger.info("Using traditional trading approach")
        
        all_signals = []
        
        if not self.strategy_manager:
            logger.warning("Strategy manager not available for traditional approach")
            return {"status": "error", "error": "No strategy manager"}
        
        # Generate signals from all strategies (traditional approach)
        for symbol, data in market_data.items():
            signals = await self.strategy_manager.generate_signals(data)
            all_signals.extend(signals)
        
        # Apply traditional validation
        validated_signals = await self._validate_traditional_signals(all_signals)
        
        # Execute trades
        executed_trades = await self._execute_traditional_trades(validated_signals)
        
        return {
            "status": "success",
            "mode": "traditional",
            "signals_generated": len(all_signals),
            "signals_validated": len(validated_signals),
            "trades_executed": len(executed_trades)
        }
    
    def _validate_regime_signal(self, signal: Any, position: Any) -> bool:
        """Enhanced validation with regime context"""
        try:
            # Basic confidence check
            if signal.confidence_score < self.config['min_confidence_threshold']:
                logger.warning(
                    "Signal rejected - low confidence",
                    strategy=signal.strategy_name,
                    confidence=signal.confidence_score,
                    threshold=self.config['min_confidence_threshold']
                )
                return False
            
            # Risk check with allocation context
            if position.max_loss_per_position > self.config['max_loss_per_trade']:
                logger.warning(
                    "Signal rejected - high risk",
                    strategy=signal.strategy_name,
                    max_loss=position.max_loss_per_position,
                    limit=self.config['max_loss_per_trade']
                )
                return False
            
            # Portfolio risk check
            if position.risk_allocation > 0.05:  # More than 5% of portfolio
                logger.warning(
                    "Signal rejected - high portfolio risk",
                    strategy=signal.strategy_name,
                    risk_allocation=position.risk_allocation
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Signal validation failed: {e}")
            return False
    
    async def _execute_adaptive_paper_trade(self, position: Any, symbol: str) -> Dict[str, Any]:
        """Execute paper trade with regime context"""
        signal = position.signal
        trade_id = f"ADAPTIVE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}_{signal.strategy_name}"
        
        trade = {
            "id": trade_id,
            "symbol": symbol,
            "strategy": signal.strategy_name,
            "type": "ADAPTIVE_PAPER",
            "status": "EXECUTED",
            "legs": len(signal.legs),
            "max_profit": signal.max_profit,
            "max_loss": signal.max_loss,
            "confidence": signal.confidence_score,
            "position_size": position.position_size,
            "allocation_weight": getattr(position, 'allocation_weight', 0.0),
            "capital_allocated": position.capital_allocation,
            "risk_allocated": position.risk_allocation,
            "reasoning": position.reasoning,
            "timestamp": datetime.now(),
            "expiry": signal.expiry_date
        }
        
        # Store enhanced position for tracking
        self.positions[trade_id] = {
            "signal": signal,
            "position": position,
            "entry_time": datetime.now(),
            "status": "OPEN",
            "current_pnl": 0.0,
            "regime_context": True
        }
        
        logger.info(
            "Adaptive paper trade executed",
            trade_id=trade_id,
            strategy=signal.strategy_name,
            symbol=symbol,
            position_size=position.position_size,
            allocation=position.allocation_weight,
            reasoning=position.reasoning[:50] + "..." if len(position.reasoning) > 50 else position.reasoning
        )
        
        return trade
    
    async def _execute_adaptive_live_trade(self, position: Any, symbol: str) -> Dict[str, Any]:
        """Execute live trade with regime context"""
        # TODO: Implement live trading via Kite Connect with regime context
        logger.warning(
            "Adaptive live trading not yet implemented",
            strategy=position.signal.strategy_name,
            symbol=symbol
        )
        return None
    
    async def _update_dashboard(self, market_data: Dict[str, MarketData]):
        """Update dashboard with latest market data"""
        try:
            # Use primary symbol for dashboard update (NIFTY typically)
            primary_data = market_data.get('NIFTY') or list(market_data.values())[0]
            await self.dashboard.update_dashboard(primary_data)
            
        except Exception as e:
            logger.error(f"Dashboard update failed: {e}")
    
    def get_adaptive_status(self) -> Dict[str, Any]:
        """Get enhanced status with regime intelligence"""
        traditional_status = self._get_traditional_status()
        
        regime_status = {}
        if self.dashboard.current_metrics:
            metrics = self.dashboard.current_metrics
            regime_status = {
                "current_regime": metrics.market_conditions.regime.value,
                "volatility_regime": metrics.market_conditions.volatility_regime.value,
                "trend_direction": metrics.market_conditions.trend_direction,
                "detection_confidence": metrics.confidence_score,
                "strategies_selected": len(metrics.strategy_allocations),
                "active_signals": metrics.active_signals_count,
                "capital_deployed": metrics.total_capital_deployed,
                "risk_utilization": metrics.risk_utilization,
                "last_updated": metrics.timestamp.isoformat()
            }
        
        portfolio_status = self.allocation_manager.get_portfolio_summary()
        
        return {
            **traditional_status,
            "mode": "adaptive" if self.config['enable_regime_intelligence'] else "traditional",
            "regime_intelligence": regime_status,
            "portfolio": portfolio_status,
            "config": self.config
        }
    
    def _get_traditional_status(self) -> Dict[str, Any]:
        """Get traditional status information"""
        strategy_count = 0
        if self.strategy_manager:
            strategy_count = len(self.strategy_manager.get_active_strategies())
            
        return {
            "active": self.active,
            "paper_trading": self.paper_trading,
            "daily_pnl": self.daily_pnl,
            "open_positions": len(self.positions),
            "strategies_active": strategy_count,
            "market_open": self._is_market_open(),
            "initial_capital": self.initial_capital
        }
    
    async def get_dashboard_display(self) -> str:
        """Get formatted dashboard display"""
        return self.dashboard.display_dashboard()
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update engine configuration"""
        self.config.update(new_config)
        logger.info("Engine configuration updated", config=self.config)
    
    def switch_to_regime_mode(self):
        """Switch to regime-based intelligence mode"""
        self.config['enable_regime_intelligence'] = True
        logger.info("Switched to regime-based intelligence mode")
    
    def switch_to_traditional_mode(self):
        """Switch to traditional strategy mode"""
        self.config['enable_regime_intelligence'] = False
        logger.info("Switched to traditional strategy mode")
    
    # Traditional methods for compatibility
    async def _initialize_broker(self):
        """Initialize broker connection"""
        # TODO: Initialize Kite Connect
        logger.info("Broker connection initialized")
    
    async def _initialize_risk_manager(self):
        """Initialize risk management system"""
        # TODO: Initialize risk manager
        logger.info("Risk manager initialized")
    
    async def _initialize_traditional_strategies(self):
        """Initialize traditional strategy manager"""
        try:
            self.strategy_manager = StrategyManager()
            logger.info("Traditional strategy manager initialized")
        except Exception as e:
            logger.error(f"Traditional strategy initialization failed: {e}")
            raise
    
    async def _fetch_market_data(self) -> Dict[str, MarketData]:
        """Fetch current market data"""
        # TODO: Implement real market data fetching via Kite Connect
        return {
            "NIFTY": MarketData(
                symbol="NIFTY",
                spot_price=24000.0,
                iv=25.0,
                volume=500000,
                oi=100000,
                last_updated=datetime.now()
            ),
            "BANKNIFTY": MarketData(
                symbol="BANKNIFTY",
                spot_price=50000.0,
                iv=30.0,
                volume=300000,
                oi=80000,
                last_updated=datetime.now()
            )
        }
    
    async def _validate_traditional_signals(self, signals: List[Any]) -> List[Any]:
        """Traditional signal validation"""
        validated = []
        for signal in signals:
            if (signal.confidence_score >= self.config['min_confidence_threshold'] and 
                signal.max_loss <= self.config['max_loss_per_trade']):
                validated.append(signal)
        return validated
    
    async def _execute_traditional_trades(self, signals: List[Any]) -> List[Dict[str, Any]]:
        """Execute traditional trades"""
        executed = []
        for signal in signals:
            if self.paper_trading:
                trade = await self._execute_traditional_paper_trade(signal)
                if trade:
                    executed.append(trade)
        return executed
    
    async def _execute_traditional_paper_trade(self, signal: Any) -> Dict[str, Any]:
        """Execute traditional paper trade"""
        trade_id = f"TRAD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{signal.symbol}"
        
        trade = {
            "id": trade_id,
            "symbol": signal.symbol,
            "strategy": signal.strategy_name,
            "type": "TRADITIONAL_PAPER",
            "status": "EXECUTED",
            "legs": len(signal.legs),
            "max_profit": signal.max_profit,
            "max_loss": signal.max_loss,
            "confidence": signal.confidence_score,
            "timestamp": datetime.now()
        }
        
        self.positions[trade_id] = {
            "signal": signal,
            "entry_time": datetime.now(),
            "status": "OPEN",
            "current_pnl": 0.0,
            "regime_context": False
        }
        
        return trade
    
    def _is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        if now.weekday() >= 5:  # Weekend
            return False
        
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def pause_trading(self):
        """Pause all trading activities"""
        self.active = False
        logger.info("Adaptive trading paused by user")
    
    def resume_trading(self):
        """Resume trading activities"""
        self.active = True
        logger.info("Adaptive trading resumed by user")
    
    async def emergency_stop(self, reason: str = "Manual stop"):
        """Emergency stop with regime context"""
        logger.critical(f"Adaptive trading emergency stop: {reason}")
        self.active = False
        # TODO: Implement position closing with regime context