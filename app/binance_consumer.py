"""
Binance WebSocket Consumer

Async WebSocket client that connects to Binance public stream API
and consumes real-time trade data for multiple cryptocurrency symbols.

Key Features:
- Multi-symbol subscription
- Automatic reconnection with exponential backoff
- Graceful shutdown handling
- Callback-based message processing
"""

# TODO: Implement BinanceWebSocketConsumer class
# - Async connection management
# - Multi-symbol stream handling  
# - JSON parsing and validation
# - Exponential backoff retry logic
# - Graceful shutdown with cleanup



import asyncio
import websockets
import json
import logging
from typing import List, Callable, Optional
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BinanceWebSocketConsumer:
    def __init__(self, symbols: List[str], on_trade_callback: Callable):
        """
        Args:
            symbols: List of trading pairs (e.g., ['BTCUSDT', 'ETHUSDT'])
            on_trade_callback: Async function to process each trade
        """
        self.symbols = [s.lower() for s in symbols]
        self.on_trade_callback = on_trade_callback
        self.base_url = "wss://stream.binance.com:9443/ws"
        self.is_running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start consuming trade data with auto-reconnection."""
        self.is_running = True
        retry_count = 0
        max_retries = 5
        
        while self.is_running and retry_count < max_retries:
            try:
                logger.info("Connecting to Binance WebSocket...")
                async with websockets.connect(self.base_url) as ws:
                    subscribe_msg = {
                        "method": "SUBSCRIBE",
                        "params": [f"{s}@trade" for s in self.symbols],
                        "id": 1
                    }
                    
                    await ws.send(json.dumps(subscribe_msg))
                    logger.info(f"✓ Subscribed to: {', '.join(self.symbols)}")
                    
                    retry_count = 0  # Reset retry count on successful connection
                    
                    
                    async for message in ws:
                        if not self.is_running:
                            break
                        
                        try:
                            data = json.loads(message)
                            
                            if data.get('e')  == 'trade':
                                trade = {
                                    'symbol': data['s'],
                                    'price': float(data['p']),
                                    'quantity': float(data['q']),
                                    'timestamp': data.get('T'),
                                    'is_buyer_maker': data.get('m')
                                }
                            
                            await self.on_trade_callback(trade)
                            
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse message: {message[:100]}")
                        except Exception as e:
                            logger.error(f"Error processing message: {e}", exc_info=True)
            except websockets.exceptions.ConnectionClosed as e:
                retry_count += 1
                wait_time = min(2 ** retry_count, 30)
                logger.warning(f"Connection closed. Retry {retry_count}/{max_retries} in {wait_time}s")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                retry_count += 1
                await asyncio.sleep(5)
            
            
            if retry_count >= max_retries:
                logger.error("Max retries reached. Stopping consumer.")
            self.is_running = False
    
    
    def stop(self):
        """Signal consumer to stop."""
        logger.info("Stopping Binance WebSocket Consumer...")
        self.is_running = False
        if self._task and not self.task.done():
            self._task.cancel()

## For testing
async def print_trade(trade):
    """Simple callback for testing."""
    symbol = trade['symbol']
    price = trade['price']
    quantity = trade['quantity']
    side = "SELL" if trade['is_buyer_maker'] else "BUY"
    time = datetime.fromtimestamp(trade['timestamp'] / 1000).strftime('%H:%M:%S')
    
    print(f"[{time}] {symbol} {side}: ${price:,.2f} x {quantity:.4f}")
    

async def main():
    """Test the consumer with multiple symbols."""
    consumer = BinanceWebSocketConsumer(
        symbols=['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
        on_trade_callback=print_trade
    )
    
    try:
        await consumer.start()
    except KeyboardInterrupt:
        consumer.stop()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())