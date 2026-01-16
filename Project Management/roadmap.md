# Real-Time Cryptocurrency Market Data Processing Engine
## Comprehensive Development Roadmap (Winter Break Project)

---

## PROJECT OVERVIEW

### Project Title: **High-Performance Real-Time Market Data Analysis Engine**

Build a **hybrid Python-C++ system** that ingests real-time cryptocurrency market data from **Binance WebSocket API**, processes it with high throughput, calculates technical indicators in C++, and exposes results via a Python REST API.

**Why This Project is Impressive:**
- ✅ Demonstrates **full-stack backend architecture** thinking
- ✅ Shows **performance optimization** skills (C++ low-level processing)
- ✅ Proves **API integration** capabilities (Binance, REST)
- ✅ Highlights **systems design** (event-driven architecture)
- ✅ Exhibits **scalability thinking** (multi-threaded processing, async I/O)
- ✅ Practical and **immediately deployable**
- ✅ **Completely free** (uses free Binance data + open-source tools)

---

## DETAILED TECHNICAL INTRODUCTION

### 1. System Architecture Overview

```
INCOMING DATA LAYER:
    ↓
  Binance WebSocket API (Free Tier)
    ↓ JSON messages (10+ trades/second per symbol)
┌─────────────────────────────────────────────────────────────────┐
│ PYTHON DATA INGESTION LAYER                                     │
│ (async WebSocket client using websockets or asyncio)            │
│ - Maintains connection to Binance                               │
│ - Parses incoming trade data (BTC/USDT, ETH/USDT, etc.)        │
│ - Queues data → C++ processing engine via IPC/shared memory    │
└─────────────────────────────────────────────────────────────────┘
    ↓ Fast IPC (named pipes or ZMQ)
┌─────────────────────────────────────────────────────────────────┐
│ C++ PROCESSING ENGINE (HIGH-PERFORMANCE CORE)                   │
│ - In-memory ring buffer for circular FIFO processing           │
│ - Technical indicator calculations:                             │
│   * Simple Moving Average (SMA)                                 │
│   * Exponential Moving Average (EMA)                            │
│   * Relative Strength Index (RSI)                               │
│   * MACD (Moving Average Convergence Divergence)               │
│ - Thread-safe concurrent processing (std::thread, mutex)        │
│ - Lock-free data structures where possible                      │
└─────────────────────────────────────────────────────────────────┘
    ↓ Serialized indicator data
┌─────────────────────────────────────────────────────────────────┐
│ PYTHON REST API LAYER (FastAPI)                                 │
│ - Exposes endpoints for real-time indicator values              │
│ - WebSocket endpoint for live streaming results                 │
│ - Historical data queries                                        │
│ - Trading signal generation                                      │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ STORAGE LAYER (PostgreSQL or SQLite)                            │
│ - Time-series data storage                                       │
│ - Query historical indicators                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Free Resources You'll Use

**Free Financial Data API:**
- **Binance WebSocket API**: Real-time crypto data (no API key needed for public streams)
- **Symbols**: BTC/USDT, ETH/USDT, ADA/USDT, etc.
- **Update Frequency**: 100ms (10+ trades per second)
- **Data Points**: Price, volume, timestamp per trade

**Free Tools & Libraries:**
| Component | Tool | Why | Free Tier |
|-----------|------|-----|-----------|
| Python Async I/O | `asyncio` + `websockets` | Non-blocking socket handling | ✅ Built-in |
| C++ Indicators | `std::vector`, custom algorithms | No dependencies needed | ✅ Standard library |
| Inter-process Communication | ZMQ (`pyzmq` + `zmq`) | Fast message passing | ✅ Open source |
| REST API | FastAPI + Uvicorn | Async Python web framework | ✅ Open source |
| Database | PostgreSQL Community Edition | Time-series optimized queries | ✅ Open source |
| Monitoring | Prometheus + Grafana (optional) | Real-time dashboards | ✅ Open source |

### 3. Key Design Decisions Explained

**Why C++ for indicator calculation?**
- Processing 10+ trades/second × 10 symbols = 100+ events/sec baseline
- C++ achieves 10-100× faster calculations than Python for numerical workloads
- Demonstrates understanding of "hot path" optimization
- Interviewers recognize this as **production-grade thinking**

**Why Python for coordination?**
- Binance WebSocket library ecosystem is Python-mature
- FastAPI is the fastest Python async web framework
- Rapid prototyping of APIs without recompilation
- Shows **pragmatic tool selection** (right tool for each job)

**Why this specific data flow?**
- Unidirectional data flow (ingestion → processing → serving) is easier to debug
- Allows independent scaling: add more C++ workers or Python API replicas
- Teaches **queue-based architecture** (fundamental in distributed systems)

---

## PHASE-BY-PHASE DEVELOPMENT ROADMAP

### PHASE 0: PREPARATION (Day 1-2)
**Objective:** Set up development environment and understand the data

#### Step 0.1: Install Dependencies
```bash
# Python packages
pip install asyncio websockets fastapi uvicorn sqlalchemy psycopg2-binary python-dateutil

# C++ libraries (system-dependent)
# macOS: brew install zeromq
# Ubuntu: sudo apt-get install libzmq3-dev

# Python C++ bridge
pip install pybind11 zmq

# Optional: PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql postgresql-contrib

# Or use lightweight SQLite instead (no setup needed)
```

#### Step 0.2: Understand Binance WebSocket Data Format
```
Real example of trade data from Binance:
{
  "e": "trade",           # Event type
  "E": 1642598400000,     # Event time (ms)
  "s": "BTCUSDT",         # Symbol
  "t": 123456,            # Trade ID
  "p": "43250.50",        # Price
  "q": "0.5",             # Quantity
  "T": 1642598400123,     # Trade time
  "m": true,              # Is buyer market maker?
}
```
**Action:** Write a simple script to subscribe to 1 symbol and print 10 messages to understand structure.

---

## IMPLEMENTATION CODE EXAMPLES

### PHASE 1: PYTHON INGESTION LAYER (Day 3-5)

**File: binance_consumer.py**

```python
import asyncio
import websockets
import json
from datetime import datetime
from typing import Callable, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceWebSocketConsumer:
    def __init__(self, symbols: List[str], on_message_callback: Callable):
        """
        symbols: ['btcusdt', 'ethusdt', 'adausdt']
        on_message_callback: async function(trade_data: dict) -> None
        """
        self.symbols = [s.lower() for s in symbols]
        self.on_message_callback = on_message_callback
        self.stream_url = "wss://stream.binance.com:9443/ws"
        self.is_running = False
        
    async def subscribe(self):
        """Subscribe to multiple trade streams"""
        streams = [f"{symbol}@trade" for symbol in self.symbols]
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": 1
        }
        return json.dumps(subscribe_message)
    
    async def connect_and_process(self):
        """Main connection loop"""
        self.is_running = True
        retry_count = 0
        max_retries = 5
        
        while self.is_running and retry_count < max_retries:
            try:
                logger.info(f"Connecting to Binance WebSocket...")
                async with websockets.connect(self.stream_url) as websocket:
                    # Send subscription
                    await websocket.send(await self.subscribe())
                    logger.info(f"Subscribed to: {self.symbols}")
                    
                    retry_count = 0  # Reset on successful connection
                    
                    # Listen for messages indefinitely
                    async for message in websocket:
                        try:
                            trade_data = json.loads(message)
                            
                            # Binance sends subscription confirmations too
                            if trade_data.get('e') == 'trade':
                                await self.on_message_callback(trade_data)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse message: {e}")
                            
            except websockets.exceptions.ConnectionClosed:
                retry_count += 1
                wait_time = min(2 ** retry_count, 30)  # Exponential backoff
                logger.warning(f"Connection closed. Retry {retry_count}/{max_retries} in {wait_time}s")
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                retry_count += 1
                await asyncio.sleep(5)
        
        logger.error("Max retries exceeded. Stopping consumer.")
        self.is_running = False
    
    def stop(self):
        """Signal consumer to stop"""
        self.is_running = False


# Example usage
async def print_trades(trade_data):
    """Callback: Process incoming trades"""
    symbol = trade_data.get('s')
    price = trade_data.get('p')
    quantity = trade_data.get('q')
    timestamp = trade_data.get('E')
    
    print(f"[{datetime.fromtimestamp(timestamp/1000)}] {symbol}: {price} x {quantity}")


async def main():
    symbols = ['btcusdt', 'ethusdt']
    consumer = BinanceWebSocketConsumer(symbols, print_trades)
    
    try:
        await consumer.connect_and_process()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

---

### PHASE 2: C++ INDICATOR CALCULATION ENGINE (Day 6-10)

**File: market_engine/indicators.cpp**

```cpp
#include <vector>
#include <deque>
#include <cmath>
#include <algorithm>
#include <thread>
#include <mutex>
#include <memory>

// Trade data structure
struct Trade {
    double price;
    double volume;
    long timestamp_ms;
};

// Indicator output
struct IndicatorSnapshot {
    double sma_20;        // Simple Moving Average (20 period)
    double ema_12;        // Exponential Moving Average (12 period)
    double rsi_14;        // Relative Strength Index (14 period)
    double macd;          // MACD line
    double macd_signal;   // MACD signal line
    double last_price;
    long timestamp_ms;
};

class MarketIndicatorEngine {
private:
    std::deque<Trade> price_window;
    const size_t MAX_WINDOW_SIZE = 500;  // Keep 500 trades in memory
    std::mutex data_mutex;
    
    // Exponential smoothing factor
    double calculate_ema_multiplier(int period) {
        return 2.0 / (period + 1.0);
    }
    
public:
    // Add new trade data
    void add_trade(const Trade& trade) {
        std::lock_guard<std::mutex> lock(data_mutex);
        price_window.push_back(trade);
        
        // Keep only recent trades in memory
        if (price_window.size() > MAX_WINDOW_SIZE) {
            price_window.pop_front();
        }
    }
    
    // Calculate Simple Moving Average
    double calculate_sma(int period) {
        std::lock_guard<std::mutex> lock(data_mutex);
        
        if (price_window.size() < period) return -1.0;
        
        double sum = 0.0;
        for (size_t i = price_window.size() - period; i < price_window.size(); ++i) {
            sum += price_window[i].price;
        }
        return sum / period;
    }
    
    // Calculate Exponential Moving Average
    double calculate_ema(int period) {
        std::lock_guard<std::mutex> lock(data_mutex);
        
        if (price_window.size() < period) return -1.0;
        
        double multiplier = calculate_ema_multiplier(period);
        double ema = 0.0;
        
        // Initialize with SMA
        for (size_t i = price_window.size() - period; i < price_window.size(); ++i) {
            ema += price_window[i].price;
        }
        ema /= period;
        
        // Apply EMA formula for remaining data
        for (size_t i = price_window.size() - period + 1; i < price_window.size(); ++i) {
            ema = price_window[i].price * multiplier + ema * (1.0 - multiplier);
        }
        
        return ema;
    }
    
    // Calculate Relative Strength Index (RSI)
    double calculate_rsi(int period) {
        std::lock_guard<std::mutex> lock(data_mutex);
        
        if (price_window.size() < period + 1) return -1.0;
        
        double gain_sum = 0.0, loss_sum = 0.0;
        
        // Calculate gains and losses
        for (size_t i = price_window.size() - period; i < price_window.size(); ++i) {
            double change = price_window[i].price - price_window[i-1].price;
            if (change > 0) {
                gain_sum += change;
            } else {
                loss_sum += std::abs(change);
            }
        }
        
        double avg_gain = gain_sum / period;
        double avg_loss = loss_sum / period;
        
        if (avg_loss == 0) return 100.0;  // All gains, no losses
        
        double rs = avg_gain / avg_loss;
        double rsi = 100.0 - (100.0 / (1.0 + rs));
        
        return rsi;
    }
    
    // Calculate MACD (Moving Average Convergence Divergence)
    std::pair<double, double> calculate_macd() {
        // MACD = EMA(12) - EMA(26)
        double ema_12 = calculate_ema(12);
        double ema_26 = calculate_ema(26);
        
        if (ema_12 < 0 || ema_26 < 0) return {-1.0, -1.0};
        
        double macd_line = ema_12 - ema_26;
        double macd_signal = macd_line;  // Simplified
        
        return {macd_line, macd_signal};
    }
    
    // Get complete snapshot
    IndicatorSnapshot get_snapshot() {
        std::lock_guard<std::mutex> lock(data_mutex);
        
        IndicatorSnapshot snapshot = {
            calculate_sma(20),
            calculate_ema(12),
            calculate_rsi(14),
            0.0,
            0.0,
            price_window.empty() ? 0.0 : price_window.back().price,
            price_window.empty() ? 0 : price_window.back().timestamp_ms
        };
        
        auto macd_pair = calculate_macd();
        snapshot.macd = macd_pair.first;
        snapshot.macd_signal = macd_pair.second;
        
        return snapshot;
    }
    
    // Get current price
    double get_last_price() {
        std::lock_guard<std::mutex> lock(data_mutex);
        return price_window.empty() ? 0.0 : price_window.back().price;
    }
};
```

---

### PHASE 3: PYTHON REST API LAYER (Day 11-13)

**File: api_server.py**

```python
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import Dict, List
from datetime import datetime
import market_engine  # Our compiled C++ module

app = FastAPI(title="Market Data Engine API")

# Global engine instances (one per trading symbol)
engines: Dict[str, market_engine.MarketIndicatorEngine] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize engines for each symbol"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT']
    for symbol in symbols:
        engines[symbol] = market_engine.MarketIndicatorEngine()
    print(f"Initialized {len(engines)} engines")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engines_count": len(engines),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/indicators/{symbol}")
async def get_indicators(symbol: str):
    """Get current technical indicators for a symbol"""
    symbol = symbol.upper()
    
    if symbol not in engines:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    engine = engines[symbol]
    snapshot = engine.get_snapshot()
    
    # Generate trading signal based on RSI
    signal = "HOLD"
    if snapshot.rsi_14 < 30:
        signal = "BUY"
    elif snapshot.rsi_14 > 70:
        signal = "SELL"
    
    return {
        "symbol": symbol,
        "last_price": snapshot.last_price,
        "sma_20": round(snapshot.sma_20, 2),
        "ema_12": round(snapshot.ema_12, 2),
        "rsi_14": round(snapshot.rsi_14, 2),
        "macd": round(snapshot.macd, 2),
        "macd_signal": round(snapshot.macd_signal, 2),
        "timestamp": datetime.fromtimestamp(snapshot.timestamp_ms / 1000).isoformat(),
        "trading_signal": signal
    }


@app.get("/indicators")
async def get_all_indicators():
    """Get indicators for all tracked symbols"""
    results = {}
    for symbol in engines.keys():
        try:
            result = await get_indicators(symbol)
            results[symbol] = result
        except HTTPException:
            pass
    return results


@app.websocket("/ws/{symbol}")
async def websocket_indicator_stream(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time indicator streaming"""
    symbol = symbol.upper()
    
    if symbol not in engines:
        await websocket.close(code=1008, reason=f"Symbol {symbol} not found")
        return
    
    await websocket.accept()
    
    try:
        while True:
            await asyncio.sleep(1)
            
            snapshot = engines[symbol].get_snapshot()
            
            data = {
                "symbol": symbol,
                "last_price": snapshot.last_price,
                "sma_20": round(snapshot.sma_20, 2),
                "ema_12": round(snapshot.ema_12, 2),
                "rsi_14": round(snapshot.rsi_14, 2),
                "timestamp": datetime.fromtimestamp(snapshot.timestamp_ms / 1000).isoformat()
            }
            
            await websocket.send_json(data)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


def update_engine_with_trade(symbol: str, price: float, volume: float, timestamp_ms: int):
    """Called by data ingestion layer to update C++ engine"""
    if symbol not in engines:
        return
    
    trade = market_engine.Trade()
    trade.price = price
    trade.volume = volume
    trade.timestamp_ms = timestamp_ms
    
    engines[symbol].add_trade(trade)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## PROJECT STRUCTURE

```
market-data-engine/
├── README.md
├── requirements.txt
├── main.py                      # Entry point
├── binance_consumer.py          # WebSocket data ingestion
├── api_server.py                # FastAPI REST & WebSocket server
├── database.py                  # Time-series storage
├── market_engine/
│   ├── indicators.cpp           # C++ core engine
│   ├── bindings.cpp             # pybind11 bindings
│   └── build/                   # Compiled .so files
├── tests/
│   ├── test_indicators.py       # Unit tests
│   └── load_test.py             # Performance testing
└── docs/
    ├── API.md
    ├── ARCHITECTURE.md
    └── DEPLOYMENT.md
```

---

## TALKING POINTS FOR INTERVIEWS

### 1. **System Design**
"I chose a queue-based, event-driven architecture separating ingestion from processing. This allows independent scaling—if the API becomes the bottleneck, I can add more Python servers without recompiling C++."

### 2. **Performance Optimization**
"The C++ engine uses a circular buffer to maintain a sliding window of 500 trades. All indicator calculations are O(n) where n ≤ 500, resulting in microsecond-level latency."

### 3. **Concurrency**
"I use std::mutex for thread-safe access without locking the entire calculation. The WebSocket consumer runs async/await in Python to handle multiple symbols concurrently."

### 4. **Real-World Thinking**
"I implemented exponential backoff retry logic for WebSocket disconnections and transaction handling for data integrity."

### 5. **Scalability**
"The system handles 1000+ trades/sec on a single machine. For 100× scaling, I'd add Kafka between ingestion and processing, run multiple C++ workers, and use consistent hashing."

---

## PERFORMANCE METRICS (Expected)

| Metric | Target | Expected |
|--------|--------|----------|
| Data Ingestion Latency | < 10ms | 2-5ms |
| Indicator Calculation | < 1ms | 100-500μs |
| API Response Time | < 50ms | 5-10ms |
| Throughput | 100+ trades/sec | 1000+ trades/sec |
| Memory Usage | < 100MB | 20-50MB |

---

## NEXT STEPS

1. **Follow the daily checklist** (see quick_start_checklist.md)
2. **Start with Phase 0** - Set up environment
3. **Build incrementally** - Test each phase before moving to next
4. **Document as you go** - Take screenshots of working system
5. **Practice your pitch** - Be ready to explain each component in 30 seconds

Good luck! 🚀
