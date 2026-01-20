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
import signal
import logging
from app.config import settings
from app.binance_consumer import BinanceWebSocketConsumer
from app.api_server import app
from app.services.orchestration import OrchestrationService
import uvicorn


logging.basicConfig(
    level = getattr(logging, settings.log_level),
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def run_consumer(orchestration: OrchestrationService, shutdown_event: asyncio.Event):
    """Run Binance WebSocket Consumer."""
    symbols = settings.symbols.split(",")
    
    async def on_trade(trade_data: dict):
        await orchestration.handle_trade(trade_data)
    
    consumer = BinanceWebSocketConsumer(symbols, on_trade_callback=on_trade)
    
    try:
        # Start consumer as a task
        consumer_task = asyncio.create_task(consumer.start())
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        logger.info("Stopping consumer...")
        consumer.stop()
        
        # Wait for consumer to finish with timeout
        try:
            await asyncio.wait_for(consumer_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Consumer didn't stop in time, forcing cancellation...")
            consumer_task.cancel()
            await asyncio.gather(consumer_task, return_exceptions=True)
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled")
        raise
    
async def run_api_server(shutdown_event: asyncio.Event):
    """Run FastAPI server using Uvicorn."""
    config = uvicorn.Config(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=1,  # Force single worker for proper shutdown
        log_level=settings.log_level.lower(),
        lifespan="on"
    )
    server = uvicorn.Server(config)
    
    # Start server in background
    server_task = asyncio.create_task(server.serve())
    
    # Wait for shutdown signal
    await shutdown_event.wait()
    
    logger.info("Stopping API server...")
    server.should_exit = True
    
    # Wait for server to finish
    try:
        await asyncio.wait_for(server_task, timeout=10.0)
    except asyncio.TimeoutError:
        logger.warning("API server didn't stop in time, forcing...")
        server_task.cancel()
        await asyncio.gather(server_task, return_exceptions=True)
    

async def main():
    """Run both consumer and API server concurrently."""
    logger.info("Starting Market Data Engine...")
    logger.info(f"Symbols: {settings.symbols}")
    
    # Initialize orchestration service
    orchestration = OrchestrationService()
    
    # Make orchestration available to API server
    import app.api_server
    app.api_server.orchestration = orchestration
    
    # Create shutdown event
    shutdown_event = asyncio.Event()
    
    def signal_handler():
        """Handle shutdown signals gracefully."""
        logger.info("Shutdown signal received, cleaning up...")
        shutdown_event.set()
    
    # Register signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        # Start both services
        await asyncio.gather(
            run_consumer(orchestration, shutdown_event),
            run_api_server(shutdown_event)
        )
    except asyncio.CancelledError:
        logger.info("Tasks cancelled")
    finally:
        # Remove signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(sig)
        
        logger.info("Market Data Engine shutdown complete.")
        
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Graceful shutdown already handled, suppress traceback