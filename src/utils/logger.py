"""
Lambda-Compatible Logging Infrastructure
Provides structured logging for AWS Lambda environment
"""
import logging
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
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


class LambdaLogger:
    """Lambda-compatible logger for trading operations"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_lambda_handler()
    
    def _setup_lambda_handler(self):
        """Setup console handler only (Lambda environment)"""
        
        # Console handler - works in all environments
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Use simple format for Lambda CloudWatch
        if os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
            # Lambda environment - simple format for CloudWatch
            formatter = logging.Formatter(
                '[%(levelname)s] %(asctime)s - %(name)s - %(message)s'
            )
        else:
            # Local development - structured format
            formatter = StructuredFormatter()
            
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with extra fields"""
        extra = self._prepare_extra(kwargs)
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error message with extra fields"""
        extra = self._prepare_extra(kwargs)
        self.logger.error(message, extra=extra, exc_info=kwargs.get('exc_info', False))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra fields"""
        extra = self._prepare_extra(kwargs)
        self.logger.warning(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra fields"""
        extra = self._prepare_extra(kwargs)
        self.logger.debug(message, extra=extra)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with extra fields"""
        extra = self._prepare_extra(kwargs)
        self.logger.critical(message, extra=extra)
    
    def _prepare_extra(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare extra fields for logging"""
        # Filter out special keys
        extra = {k: v for k, v in kwargs.items() if k != 'exc_info'}
        return extra


def get_logger(name: str, level: str = "INFO") -> LambdaLogger:
    """
    Get a configured logger for the given name.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured LambdaLogger instance
    """
    return LambdaLogger(name, level)


# Pre-configured loggers for common modules
trading_logger = get_logger("trading_bot.trading")
engine_logger = get_logger("trading_bot.engine")
strategy_logger = get_logger("trading_bot.strategy")
broker_logger = get_logger("trading_bot.broker")
risk_logger = get_logger("trading_bot.risk")


# For backward compatibility
def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
        stream=sys.stdout
    )
    return logging.getLogger("trading_bot")


# Default main logger
main_logger = get_logger("trading_bot.main")