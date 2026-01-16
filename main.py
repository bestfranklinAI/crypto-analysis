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
import sys
from typing import Optional

# TODO: Import modules once implemented
# from app.config import settings
# from app.binance_consumer import BinanceWebSocketConsumer
# from app.api_server import app
# from app.services.orchestration import OrchestrationService


class MarketDataEngine:
    """
    Main application coordinator.
    
    Manages lifecycle of all components and handles graceful shutdown.
    """
    
    def __init__(self):
        """Initialize the market data engine."""
        # TODO: Initialize components
        # self.orchestration_service = OrchestrationService()
        # self.consumer = BinanceWebSocketConsumer(...)
        # self.api_server = ...
        pass
    
    async def start(self) -> None:
        """
        Start all components concurrently.
        
        Raises:
            Exception: If any component fails to start
        """
        print("Starting Market Data Engine v0.1.0...")
        
        # TODO: Implement startup sequence
        # 1. Initialize C++ engines for each symbol
        # 2. Start Binance WebSocket consumer
        # 3. Start FastAPI server
        # 4. Start periodic snapshot task
        
        # Example structure:
        # await asyncio.gather(
        #     self.consumer.start(),
        #     self.api_server.start(),
        #     self.orchestration_service.run_snapshot_loop(),
        # )
        pass
    
    async def stop(self) -> None:
        """
        Gracefully shutdown all components.
        
        Ensures all data is persisted before exit.
        """
        print("Shutting down Market Data Engine...")
        
        # TODO: Implement shutdown sequence
        # 1. Stop accepting new WebSocket messages
        # 2. Process remaining messages in queue
        # 3. Save final database snapshot
        # 4. Close database connections
        # 5. Close API server
        
        print("Shutdown complete.")


async def main() -> None:
    """
    Application entrypoint.
    
    Sets up signal handlers and runs the main event loop.
    """
    engine: Optional[MarketDataEngine] = None
    
    try:
        engine = MarketDataEngine()
        
        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(shutdown(engine))
            )
        
        # Start the engine
        await engine.start()
        
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if engine:
            await engine.stop()


async def shutdown(engine: MarketDataEngine) -> None:
    """
    Handle shutdown signal.
    
    Args:
        engine: The running market data engine instance
    """
    await engine.stop()
    # Stop the event loop
    loop = asyncio.get_running_loop()
    loop.stop()


if __name__ == "__main__":
    # TODO: Add CLI argument parsing
    # - --config: Path to config file
    # - --symbols: Override symbols from CLI
    # - --log-level: Override log level
    # - --no-db: Disable database persistence
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        sys.exit(0)
