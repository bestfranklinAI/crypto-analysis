# Architecture Documentation

## System Overview

The **Market Data Engine** is a hybrid Python-C++ system designed for real-time cryptocurrency market data processing. It demonstrates enterprise-grade architecture patterns for high-performance financial data processing.

## Design Philosophy

1. **Right Tool for the Job**: Python for orchestration/APIs, C++ for compute-intensive operations
2. **Single Responsibility**: Each component has a clear, focused purpose
3. **Scalability First**: Designed to handle 1000+ trades/second across multiple symbols
4. **Production Ready**: Comprehensive error handling, logging, and monitoring

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCE                          │
│                  Binance WebSocket API (Free)                    │
│              wss://stream.binance.com:9443/ws                    │
└────────────────────────┬────────────────────────────────────────┘
                         │ JSON Trade Messages
                         │ (10+ trades/sec per symbol)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   INGESTION LAYER (Python)                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  BinanceWebSocketConsumer                              │    │
│  │  • Async WebSocket client                              │    │
│  │  • Multi-symbol subscription                           │    │
│  │  • Exponential backoff retry                           │    │
│  │  • Graceful shutdown handling                          │    │
│  └────────────────────┬───────────────────────────────────┘    │
└─────────────────────────┼────────────────────────────────────────┘
                         │ Parsed Trade Objects
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  PROCESSING LAYER (C++)                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  MarketIndicatorEngine (per symbol)                    │    │
│  │  • Sliding window trade buffer (std::deque)            │    │
│  │  • Technical indicators:                               │    │
│  │    - SMA (Simple Moving Average)                       │    │
│  │    - EMA (Exponential Moving Average)                  │    │
│  │    - RSI (Relative Strength Index)                     │    │
│  │    - MACD (Moving Average Convergence Divergence)     │    │
│  │  • Thread-safe operations (std::mutex)                 │    │
│  │  • Target: <1ms per calculation                        │    │
│  └────────────────────┬───────────────────────────────────┘    │
└─────────────────────────┼────────────────────────────────────────┘
                         │ Indicator Snapshots
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 SERVICE LAYER (Python)                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  IndicatorService                                       │    │
│  │  • Engine instance management                          │    │
│  │  • Trade routing                                       │    │
│  │  • Signal generation (BUY/SELL/HOLD)                  │    │
│  └────────────────────┬───────────────────────────────────┘    │
│                       │                                          │
│  ┌────────────────────┴───────────────────────────────────┐    │
│  │  OrchestrationService                                   │    │
│  │  • Component lifecycle management                      │    │
│  │  • Periodic database snapshots                         │    │
│  │  • Error recovery coordination                         │    │
│  └────────────────────┬───────────────────────────────────┘    │
└─────────────────────────┼────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ↓                             ↓
┌───────────────────┐         ┌──────────────────────┐
│   API LAYER       │         │  PERSISTENCE LAYER   │
│   (FastAPI)       │         │  (SQLite/SQLAlchemy) │
│                   │         │                      │
│  REST Endpoints:  │         │  • Time-series data  │
│  • /health        │         │  • Historical query  │
│  • /indicators    │         │  • Async operations  │
│  • /history       │         │                      │
│                   │         └──────────────────────┘
│  WebSocket:       │
│  • /ws/{symbol}   │
│                   │
└───────────────────┘
```

---

## Component Responsibilities

### 1. Binance Consumer (`app/binance_consumer.py`)
**Purpose**: Reliable real-time data ingestion from Binance

**Responsibilities**:
- Establish and maintain WebSocket connections
- Subscribe to multiple symbol streams
- Parse and validate incoming JSON messages
- Forward trades to indicator service
- Handle reconnection with exponential backoff
- Graceful shutdown on SIGTERM/SIGINT

**Key Design Decisions**:
- Uses `asyncio` + `websockets` for non-blocking I/O
- Callback-based architecture for decoupling
- No business logic—pure data transport

### 2. Market Indicator Engine (`market_engine/*.cpp`)
**Purpose**: High-performance technical indicator calculations

**Responsibilities**:
- Maintain sliding window of recent trades (per symbol)
- Calculate technical indicators on demand
- Provide thread-safe access to indicator values
- Minimize memory allocations (use circular buffers)

**Key Design Decisions**:
- C++17 for 10-100× faster calculations than Python
- `std::deque` for O(1) push/pop on sliding window
- `std::mutex` for thread safety with minimal contention
- Header-only where possible to enable inlining

**Indicator Algorithms**:
- **SMA**: Simple arithmetic mean of last N prices
- **EMA**: Exponential weighted average with α = 2/(N+1)
- **RSI**: Relative strength = 100 - (100 / (1 + RS)), where RS = avg gain / avg loss
- **MACD**: MACD line = EMA₁₂ - EMA₂₆, Signal = EMA₉(MACD), Histogram = MACD - Signal

### 3. Indicator Service (`app/services/indicators.py`)
**Purpose**: Python wrapper around C++ engine

**Responsibilities**:
- Instantiate one `MarketIndicatorEngine` per symbol
- Route incoming trades to correct engine
- Retrieve indicator snapshots
- Generate simple trading signals based on indicator thresholds

**Key Design Decisions**:
- Maintains engine state in memory (no shared state between processes)
- Uses Python's `threading` module for concurrent access if needed
- Returns Pydantic models for type safety

### 4. API Server (`app/api_server.py`)
**Purpose**: Expose real-time and historical data via HTTP/WebSocket

**Endpoints**:
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| GET | `/indicators/{symbol}` | Current indicators for one symbol |
| GET | `/indicators` | Current indicators for all symbols |
| GET | `/history/{symbol}` | Historical indicator snapshots |
| WS | `/ws/{symbol}` | Real-time indicator stream |

**Key Design Decisions**:
- FastAPI for automatic OpenAPI docs
- Async request handlers for non-blocking I/O
- WebSocket broadcasts via `asyncio.Queue`
- CORS enabled for frontend integration

### 5. Database Layer (`app/database.py`)
**Purpose**: Persist indicator snapshots for historical queries

**Schema**:
```sql
CREATE TABLE indicator_snapshots (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    last_price REAL,
    sma REAL,
    ema REAL,
    rsi REAL,
    macd REAL,
    macd_signal REAL,
    macd_histogram REAL,
    trade_count INTEGER,
    INDEX(symbol, timestamp)
);
```

**Key Design Decisions**:
- SQLite for simplicity (can swap to PostgreSQL for production)
- SQLAlchemy async session for non-blocking DB I/O
- Write snapshots every 60 seconds (configurable)
- Retention policy: keep last 30 days (future enhancement)

---

## Data Flow Sequence

### Typical Trade Processing Flow

```
1. Binance sends trade JSON via WebSocket
   ↓
2. BinanceWebSocketConsumer.on_message()
   - Parses JSON
   - Validates required fields
   ↓
3. Calls orchestration callback with trade data
   ↓
4. OrchestrationService.handle_trade()
   - Routes to IndicatorService
   ↓
5. IndicatorService.add_trade(symbol, trade)
   - Finds correct C++ engine instance
   - Calls engine.add_trade() via pybind11
   ↓
6. C++ MarketIndicatorEngine.add_trade()
   - Locks mutex
   - Adds to sliding window deque
   - Evicts oldest trade if window full
   - Unlocks mutex
   ↓
7. (Later) API request arrives: GET /indicators/BTCUSDT
   ↓
8. IndicatorService.get_indicators(symbol)
   - Calls engine.get_snapshot()
   ↓
9. C++ calculates all indicators on-demand
   - Returns IndicatorSnapshot struct
   ↓
10. FastAPI serializes to JSON via Pydantic
   ↓
11. Response sent to client
```

### WebSocket Streaming Flow

```
1. Client connects: WS /ws/BTCUSDT
   ↓
2. API server registers connection in active_connections dict
   ↓
3. Background task runs every 1 second:
   - Calls IndicatorService.get_indicators(symbol)
   - Broadcasts snapshot to all connected clients
   ↓
4. Client disconnects
   - Connection removed from active_connections
```

---

## Threading and Concurrency Model

### Python Layer
- **Main thread**: Runs FastAPI server via `uvicorn`
- **Asyncio event loop**: Handles WebSocket connections, database I/O
- **Background tasks**: Periodic snapshot persistence, WebSocket broadcasts

### C++ Layer
- **Thread-safe**: All `MarketIndicatorEngine` methods use `std::lock_guard`
- **No async**: Pure synchronous computation (latency <1ms, no blocking needed)

### Synchronization Points
- Python GIL released during C++ calls (via pybind11)
- No shared state between symbols (each has own engine instance)
- Database writes serialized via asyncio (no concurrent writes)

---

## Performance Characteristics

### Latency Targets
| Operation | Target | Typical |
|-----------|--------|---------|
| C++ indicator calculation | <1ms | ~0.3ms |
| Trade ingestion (Python → C++) | <5ms | ~2ms |
| API response time | <50ms | ~20ms |
| WebSocket broadcast | <100ms | ~50ms |

### Throughput Targets
- **Trade ingestion**: 1000+ trades/second
- **API requests**: 500+ req/sec
- **WebSocket connections**: 100+ concurrent clients

### Memory Usage
- **Per symbol**: ~50 KB (500 trades × ~100 bytes each)
- **10 symbols**: ~500 KB + Python overhead ≈ **5 MB total**

---

## Error Handling Strategy

### Levels of Resilience

1. **Network Errors** (Binance disconnection)
   - Exponential backoff retry: 1s, 2s, 4s, ..., max 30s
   - Log all retry attempts
   - Metrics: `binance_reconnection_count`

2. **Data Validation Errors** (malformed JSON)
   - Log and skip invalid messages
   - Metrics: `invalid_trade_count`
   - Alert if >1% of messages invalid

3. **C++ Exceptions** (memory allocation, logic errors)
   - Caught in Python bindings
   - Symbol marked as unhealthy
   - Graceful degradation: return last known values

4. **Database Errors** (write failures)
   - Retry 3 times with exponential backoff
   - Fall back to in-memory only
   - Log warning, continue serving real-time data

5. **API Errors** (client timeout, bad requests)
   - Return 4xx/5xx with error details
   - Log client errors at DEBUG level
   - Log server errors at ERROR level

---

## Monitoring and Observability

### Key Metrics

**System Health**:
- `uptime_seconds`: Time since service start
- `active_symbols`: Number of symbols being tracked
- `total_trades_processed`: Lifetime counter

**Performance**:
- `trade_processing_latency_ms`: Histogram (p50, p95, p99)
- `indicator_calculation_latency_ms`: Per-symbol histogram
- `api_request_latency_ms`: Per-endpoint histogram

**Business Logic**:
- `last_price`: Gauge per symbol
- `rsi_value`: Gauge per symbol
- `trading_signals_generated`: Counter (BUY/SELL/HOLD)

**Errors**:
- `binance_connection_errors`: Counter
- `invalid_trade_messages`: Counter
- `database_write_errors`: Counter

### Logging

**Structured Logging** (via `structlog`):
```python
log.info("trade_processed", 
         symbol="BTCUSDT", 
         price=45123.50, 
         latency_ms=1.2)
```

**Log Levels**:
- **DEBUG**: Individual trade processing, detailed flow
- **INFO**: Service lifecycle, periodic summaries
- **WARNING**: Transient errors, retry attempts
- **ERROR**: Persistent errors, degraded service
- **CRITICAL**: Service-wide failures, immediate attention needed

---

## Scalability Considerations

### Current Limitations
- Single-process Python (GIL contention)
- SQLite (single writer)
- In-memory only (no persistence on restart)

### Future Enhancements

**Horizontal Scaling**:
- Shard symbols across multiple processes
- Use Redis for shared state
- Load balancer for API servers

**Database Scaling**:
- Migrate to PostgreSQL with TimescaleDB
- Implement read replicas
- Batch writes (insert 1000 rows at once)

**Compute Scaling**:
- Multi-threaded C++ engine (one thread per symbol)
- GPU acceleration for parallel indicator calculation
- Distribute C++ workers via ZMQ

---

## Security Considerations

### Current Implementation
- ✅ No authentication (public data, read-only)
- ✅ Input validation via Pydantic
- ✅ SQL injection prevention via SQLAlchemy
- ✅ WebSocket rate limiting (future)

### Production Hardening
- [ ] API key authentication (JWT)
- [ ] Rate limiting per client IP
- [ ] HTTPS/WSS only (no plain HTTP)
- [ ] Input sanitization for symbol names
- [ ] DDoS protection (Cloudflare, AWS Shield)

---

## Technology Choices Rationale

| Technology | Why? | Alternatives Considered |
|------------|------|-------------------------|
| **Python 3.13** | Mature async/await, rich library ecosystem | Go (less mature for finance), Rust (steeper learning curve) |
| **C++17** | 10-100× faster than Python for numerical compute | Cython (harder to debug), Rust (interop complexity) |
| **pybind11** | Clean Python-C++ bindings, zero-copy where possible | ctypes (manual, error-prone), SWIG (outdated) |
| **FastAPI** | Fastest Python async web framework, auto-docs | Flask (synchronous), Django (too heavy) |
| **SQLite** | Zero-config, file-based, perfect for prototypes | PostgreSQL (overkill initially), MongoDB (wrong fit) |
| **websockets** | Clean async WebSocket library | `aiohttp` (more complex), raw `asyncio` (too low-level) |
| **asyncio** | Native Python async I/O, non-blocking | Threading (GIL issues), multiprocessing (IPC overhead) |

---

## Testing Strategy

See [tests/](../tests/) for implementation details.

1. **Unit Tests**: Each component in isolation
2. **Integration Tests**: End-to-end data flow
3. **Load Tests**: Performance under realistic load
4. **Fuzz Tests**: Random inputs to find edge cases (future)

---

## Deployment Architecture

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

**Local Development**:
```
venv → Python app + uvicorn → localhost:8000
```

**Production (Docker)**:
```
Docker container → Gunicorn + uvicorn workers → Nginx reverse proxy
```

**Cloud (AWS)**:
```
ECS Fargate → ALB → Route53 → CloudFront (static assets)
```
