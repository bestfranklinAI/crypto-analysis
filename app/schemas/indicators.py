"""
Indicator Schemas

Pydantic models for indicator data structures used in API responses.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class IndicatorSnapshot(BaseModel):
    """Indicator values snapshot for a specific symbol at a point in time."""
    
    symbol: str = Field(..., description="Trading pair symbol (e.g., BTCUSDT)")
    timestamp: datetime = Field(..., description="Snapshot timestamp")

    
    # sma: Optional[float] = Field(None, description="Simple Moving Average")
    # ema: Optional[float] = Field(None, description="Exponential Moving Average")
    rsi: Optional[float] = Field(None, description="Relative Strength Index (0-100)")
    vwap: Optional[float] = Field(None, description="Volume Weighted Average Price")
    # macd: Optional[float] = Field(None, description="MACD line value")
    # macd_signal: Optional[float] = Field(None, description="MACD signal line")
    # macd_histogram: Optional[float] = Field(None, description="MACD histogram")
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "timestamp": "2026-01-16T10:30:00Z",
                "rsi": 62.5,
                "vwap": 44950.75
            }
        }


class TradingSignal(BaseModel):
    """Simple trading signal based on indicator values."""
    
    symbol: str = Field(..., description="Trading pair symbol")
    signal: str = Field(..., description="Signal type: BUY, SELL, or HOLD")
    confidence: float = Field(..., ge=0, le=1, description="Signal confidence (0-1)")
    reason: str = Field(..., description="Human-readable explanation")
    timestamp: datetime = Field(..., description="Signal generation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTCUSDT",
                "signal": "BUY",
                "confidence": 0.75,
                "reason": "RSI below 30 indicates oversold condition",
                "timestamp": "2026-01-16T10:30:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    active_symbols: int = Field(..., description="Number of symbols being tracked")
