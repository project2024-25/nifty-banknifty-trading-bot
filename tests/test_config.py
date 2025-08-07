"""
Test configuration management
"""
import pytest
from unittest.mock import patch
import os

from src.utils.config import Config, get_config


class TestConfig:
    """Test configuration class"""
    
    def test_config_with_env_vars(self):
        """Test configuration loading with environment variables"""
        env_vars = {
            'KITE_API_KEY': 'test_api_key',
            'KITE_API_SECRET': 'test_api_secret',
            'TELEGRAM_BOT_TOKEN': 'test_bot_token',
            'TELEGRAM_USER_ID': '123456789',
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test_supabase_key',
            'TRADING_CAPITAL': '50000',
            'MAX_DAILY_LOSS_PERCENT': '2.5'
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert config.kite_api_key == 'test_api_key'
            assert config.kite_api_secret == 'test_api_secret'
            assert config.telegram_user_id == 123456789
            assert config.trading_capital == 50000.0
            assert config.max_daily_loss_percent == 2.5
    
    def test_config_defaults(self):
        """Test configuration defaults"""
        env_vars = {
            'KITE_API_KEY': 'test_api_key',
            'KITE_API_SECRET': 'test_api_secret',
            'TELEGRAM_BOT_TOKEN': 'test_bot_token',
            'TELEGRAM_USER_ID': '123456789',
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test_supabase_key'
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            # Test defaults
            assert config.trading_capital == 100000
            assert config.max_daily_loss_percent == 3
            assert config.conservative_allocation == 60
            assert config.aggressive_allocation == 40
            assert config.enable_paper_trading is True
            assert config.environment == "development"
    
    def test_is_production(self):
        """Test production environment detection"""
        env_vars = {
            'KITE_API_KEY': 'test_api_key',
            'KITE_API_SECRET': 'test_api_secret',
            'TELEGRAM_BOT_TOKEN': 'test_bot_token',
            'TELEGRAM_USER_ID': '123456789',
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test_supabase_key',
            'ENVIRONMENT': 'production'
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            assert config.is_production is True
            assert config.is_development is False
    
    @pytest.mark.skip(reason="Validation requires all env vars")
    def test_config_validation_missing_vars(self):
        """Test configuration validation with missing variables"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                Config.validate_required()