"""
Logging Infrastructure
Provides structured logging for the trading bot
"""
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add extra fields if present
        extra_fields = [
            'trade_id', 'strategy', 'symbol', 'order_id', 
            'user_id', 'session_id', 'correlation_id',
            'pnl', 'quantity', 'price'
        ]
        
        for field in extra_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class TradingLogger:
    """Enhanced logger for trading operations"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers"""
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = StructuredFormatter()
        console_handler.setFormatter(console_formatter)
        
        # File handler for persistent logging
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with extra context"""
        self.logger.info(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra context"""
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra context"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with extra context"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with extra context"""
        self.logger.critical(message, extra=kwargs)
    
    def trade_executed(self, trade_data: Dict[str, Any]):
        """Log trade execution with structured data"""
        self.info(
            "Trade executed",
            trade_id=trade_data.get('id'),
            strategy=trade_data.get('strategy'),
            symbol=trade_data.get('symbol'),
            price=trade_data.get('price'),
            quantity=trade_data.get('quantity'),
            pnl=trade_data.get('pnl')
        )
    
    def order_placed(self, order_data: Dict[str, Any]):
        """Log order placement with structured data"""
        self.info(
            "Order placed",
            order_id=order_data.get('id'),
            symbol=order_data.get('symbol'),
            order_type=order_data.get('type'),
            price=order_data.get('price'),
            quantity=order_data.get('quantity')
        )
    
    def strategy_signal(self, signal_data: Dict[str, Any]):
        """Log strategy signal generation"""
        self.info(
            "Strategy signal generated",
            strategy=signal_data.get('strategy'),
            symbol=signal_data.get('symbol'),
            signal_type=signal_data.get('type'),
            confidence=signal_data.get('confidence'),
            timestamp=signal_data.get('timestamp')
        )
    
    def risk_check(self, check_result: Dict[str, Any]):
        """Log risk management checks"""
        level = "warning" if not check_result.get('passed') else "info"
        getattr(self, level)(
            f"Risk check {'passed' if check_result.get('passed') else 'failed'}",
            check_type=check_result.get('type'),
            reason=check_result.get('reason'),
            current_value=check_result.get('current_value'),
            limit=check_result.get('limit')
        )
    
    def system_health(self, health_data: Dict[str, Any]):
        """Log system health metrics"""
        self.info(
            "System health check",
            status=health_data.get('status'),
            uptime=health_data.get('uptime'),
            memory_usage=health_data.get('memory_usage'),
            api_latency=health_data.get('api_latency'),
            active_positions=health_data.get('active_positions')
        )


# Global logger instances
def get_logger(name: str, level: str = "INFO") -> TradingLogger:
    """Get logger instance for a module"""
    return TradingLogger(name, level)


# Pre-configured loggers for different components
main_logger = get_logger("trading_bot.main")
strategy_logger = get_logger("trading_bot.strategy")
risk_logger = get_logger("trading_bot.risk")
api_logger = get_logger("trading_bot.api")
telegram_logger = get_logger("trading_bot.telegram")
database_logger = get_logger("trading_bot.database")


# Performance logging decorator
def log_performance(func):
    """Decorator to log function performance"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger = get_logger(f"performance.{func.__module__}.{func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Function executed successfully",
                function=func.__name__,
                duration_seconds=duration,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.error(
                f"Function execution failed",
                function=func.__name__,
                duration_seconds=duration,
                error=str(e),
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            
            raise
    
    return wrapper