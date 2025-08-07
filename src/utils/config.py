"""
Configuration Management
Handles environment variables and application settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """Application configuration from environment variables"""
    
    # Kite Connect Configuration
    kite_api_key: str = Field(..., env="KITE_API_KEY")
    kite_api_secret: str = Field(..., env="KITE_API_SECRET")
    kite_access_token: Optional[str] = Field(None, env="KITE_ACCESS_TOKEN")
    kite_request_token: Optional[str] = Field(None, env="KITE_REQUEST_TOKEN")
    
    # Telegram Configuration
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_user_id: int = Field(..., env="TELEGRAM_USER_ID")
    
    # Database Configuration
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    supabase_service_key: Optional[str] = Field(None, env="SUPABASE_SERVICE_KEY")
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field("ap-south-1", env="AWS_DEFAULT_REGION")
    
    # Trading Configuration
    trading_capital: float = Field(100000, env="TRADING_CAPITAL")
    max_daily_loss_percent: float = Field(3, env="MAX_DAILY_LOSS_PERCENT")
    conservative_allocation: float = Field(60, env="CONSERVATIVE_ALLOCATION")
    aggressive_allocation: float = Field(40, env="AGGRESSIVE_ALLOCATION")
    risk_per_trade: float = Field(0.02, env="RISK_PER_TRADE")
    max_positions: int = Field(5, env="MAX_POSITIONS")
    
    # Strategy Configuration
    enable_iron_condor: bool = Field(True, env="ENABLE_IRON_CONDOR")
    enable_credit_spreads: bool = Field(True, env="ENABLE_CREDIT_SPREADS")
    enable_straddles: bool = Field(False, env="ENABLE_STRADDLES")
    enable_directional: bool = Field(False, env="ENABLE_DIRECTIONAL")
    
    # Feature Flags
    enable_paper_trading: bool = Field(True, env="ENABLE_PAPER_TRADING")
    enable_ml_predictions: bool = Field(False, env="ENABLE_ML_PREDICTIONS")
    enable_youtube_analysis: bool = Field(True, env="ENABLE_YOUTUBE_ANALYSIS")
    enable_real_time_data: bool = Field(True, env="ENABLE_REAL_TIME_DATA")
    
    # Monitoring
    log_level: str = Field("INFO", env="LOG_LEVEL")
    enable_cloudwatch: bool = Field(False, env="ENABLE_CLOUDWATCH")
    webhook_url: Optional[str] = Field(None, env="WEBHOOK_URL")
    
    # YouTube API
    youtube_api_key: Optional[str] = Field(None, env="YOUTUBE_API_KEY")
    
    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @classmethod
    def validate_required(cls) -> None:
        """Validate all required credentials are present"""
        required_fields = [
            'kite_api_key', 'kite_api_secret',
            'telegram_bot_token', 'telegram_user_id',
            'supabase_url', 'supabase_key'
        ]
        
        config = cls()
        missing_fields = []
        
        for field in required_fields:
            if not getattr(config, field):
                missing_fields.append(field.upper())
        
        if missing_fields:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"


# Global configuration instance
try:
    config = Config()
except Exception:
    # For cases where .env file doesn't exist yet
    config = None


def get_config() -> Config:
    """Get configuration instance"""
    global config
    if config is None:
        config = Config()
    return config


def validate_config():
    """Validate configuration on startup"""
    try:
        Config.validate_required()
        return True
    except ValueError as e:
        print(f"Configuration validation failed: {e}")
        return False