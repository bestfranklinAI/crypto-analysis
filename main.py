"""
Market Data Engine - Main Entrypoint

This script starts the complete market data processing pipeline:
1. Initializes the C++ indicator engine instances
2. Starts the Binance WebSocket consumer
3. Launches the FastAPI server
4. Coordinates periodic database snapshots

Run with: python main.py
"""

import asyncio
import logging
from app.config import settings
from app.binance_consumer import BinanceWebSocketConsumer
from app.api_server import app, orchestration
import uvicorn


logging.basicConfig(
    level = getattr(logging, settings.log_level),
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def main():
    """Run Binance WebSocekt Consumer"""
    symbols = settings.symbols.split(",")
    
    async def on_trade(trade_data: dict):
        await orchestration.handle_trade(trade_data)
    
    
    consumer = BinanceWebSocketConsumer(symbols, on_trade_callback=on_trade)
    await consumer.start()
    
async def run_api_server():
    """Run FastAPI server using Uvicorn."""
    config = uvicorn.Config(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
        lifespan="on"
    )
    server = uvicorn.Server(config)
    await server.serve()
    
    
if __name__ == "__main__":
    asyncio.run(run_api_server())