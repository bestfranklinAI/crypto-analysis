"""
FastAPI Server

REST API and WebSocket endpoints for accessing real-time
and historical indicator data.

Endpoints:
- GET /health - Health check
- GET /indicators/{symbol} - Get indicators for a specific symbol
- GET /indicators - Get indicators for all symbols
- GET /history/{symbol} - Get historical indicator snapshots
- WS /ws/{symbol} - Stream live indicator updates
"""

# TODO: Implement FastAPI application
# - Health check endpoint
# - REST endpoints for indicators
# - WebSocket endpoint for streaming
# - Error handling and validation
# - CORS configuration



from fastapi import FastAPI, HTTPException
from app.services.orchestration import OrchestrationService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title = "Market Data Engine")

orchestration: OrchestrationService = None

@app.on_event("startup")
async def startup_event():
    global orchestration
    orchestration = OrchestrationService()
    logger.info("FastAPI server started.")
    
    
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "symbols": settings.symbols.split(",")}

@app.get("/indicators/{symbol}")
async def get_indicators(symbol: str):
    """Get indicators for a specific symbol."""
    indicators = orchestration.get_indicators(symbol.upper())
    if indicators is None or not indicators.get("is_valid"):
        raise HTTPException(status_code=404, detail=f"No data available for symbol {symbol}")
    return indicators


@app.get("/indicators")
async def get_all_indicators():
    """Get indicators for all symbols."""
    results = {}
    for symbol in settings.symbols.split(","):
        indicators = orchestration.get_indicators(symbol.upper())
        if indicators and indicators.get("is_valid"):
            results[symbol.upper()] = indicators
    return results

