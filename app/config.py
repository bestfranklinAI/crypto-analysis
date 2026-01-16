"""
Configuration Module

Manages application configuration from environment variables and .env files.
Uses pydantic-settings for type-safe configuration management.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    
    # Binance WebSocket
    binance_ws_url: str = "wss://stream.binance.com:9443/ws"
    symbols: str = "BTCUSDT,ETHUSDT"
    
    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./market_data.db"
    
    # Indicator Settings
    max_trade_window: int = 500
    sma_period: int = 20
    ema_period: int = 12
    rsi_period: int = 14
    macd_fast_period: int = 12
    macd_slow_period: int = 26
    macd_signal_period: int = 9
    
    # Performance
    enable_historical_storage: bool = True
    snapshot_interval_seconds: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def symbol_list(self) -> List[str]:
        """Parse comma-separated symbols into a list."""
        return [s.strip() for s in self.symbols.split(",")]


# Global settings instance
settings = Settings()
