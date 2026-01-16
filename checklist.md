# Quick Start Checklist: Real-Time Market Data Engine
## Day-by-Day Development Guide

---

## Pre-Project Setup (30 mins)

- [ ] Clone/create project directory
- [ ] Create Python virtual environment: `python3 -m venv venv && source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify Binance API access (no authentication needed for public streams)
- [ ] Install C++ compiler: `g++` (Linux) / `clang` (macOS) / `MSVC` (Windows)

---

## Phase 0: Preparation (Days 1-2) ✓

### Day 1: Environment & Testing
- [ ] Set up project structure
- [ ] Write test_binance_connection.py - verify WebSocket connectivity
- [ ] Run simple 5-second test to confirm data flowing in
- [ ] Print sample trade data to understand JSON structure

### Day 2: Understand the Data Format
- [ ] Print full JSON structure of Binance trades
- [ ] Identify key fields: `p` (price), `q` (quantity), `E` (timestamp), `s` (symbol)
- [ ] Write simple statistics script (min/max/average price over 100 trades)
- [ ] Test with 1 symbol, then 3 symbols

---

## Phase 1: Python Ingestion (Days 3-5) ✓

### Day 3: Basic WebSocket Consumer
- [ ] Implement BinanceWebSocketConsumer class
  - [ ] Async WebSocket connection management
  - [ ] JSON parsing for trade data
  - [ ] Support multiple symbols
- [ ] Test with 1 symbol for 60 seconds
- [ ] Verify: Prints ~10 trades per second

**Deliverable:** python binance_consumer.py runs for 5 mins without crashing

### Day 4: Add Robustness
- [ ] Implement exponential backoff retry logic (2^n, max 30s)
- [ ] Add Python logging module integration
- [ ] Test connection drop recovery (kill network)
- [ ] Add graceful shutdown with KeyboardInterrupt handling

### Day 5: Callback Integration
- [ ] Implement callback-based message handling
- [ ] Test with 5 symbols simultaneously
- [ ] Prepare for API integration (callback will call update_engine_with_trade)
- [ ] Verify: No dropped messages, consistent throughput

**Deliverable:** Reliable 24/7 consumer ready for production

---

## Phase 2: C++ Engine (Days 6-10) ✓

### Day 6: Set Up C++ Build
- [ ] Install pybind11: pip install pybind11
- [ ] Create market_engine/ directory structure
- [ ] Write simple Hello World C++ module
- [ ] Verify compilation and Python import works
- [ ] Run: python -c "import market_engine; print('OK')"

### Day 7: Implement Core Data Structures
- [ ] Define Trade struct (price, volume, timestamp)
- [ ] Define IndicatorSnapshot struct
- [ ] Implement MarketIndicatorEngine class
- [ ] Implement add_trade() method
- [ ] Create pybind11 bindings
- [ ] Verify: Can add trades and read price from Python

### Day 8: Implement SMA & EMA
- [ ] Implement calculate_sma(period)
- [ ] Implement calculate_ema(period)
- [ ] Write unit tests with known data
- [ ] Test: All same price input → should return that price
- [ ] Verify correctness against manual calculations

### Day 9: Implement RSI & MACD
- [ ] Implement calculate_rsi(period)
  - [ ] Test: pure uptrend → RSI > 70
  - [ ] Test: pure downtrend → RSI < 30
- [ ] Implement calculate_macd()
- [ ] Test both indicators with realistic data

### Day 10: Performance Optimization
- [ ] Profile indicator calculation time
- [ ] Verify: All calculations < 1ms on 500-trade window
- [ ] Add thread safety with std::mutex
- [ ] Test concurrent access: multiple readers, single writer
- [ ] Load test: Process 1000+ trades/sec without bottleneck

**Deliverable:** High-performance, thread-safe C++ engine

---

## Phase 3: REST API (Days 11-13) ✓

### Day 11: FastAPI Server Skeleton
- [ ] Create api_server.py with FastAPI app
- [ ] Implement @app.on_event("startup") to initialize engines
- [ ] Implement /health endpoint
- [ ] Run: uvicorn api_server:app --reload
- [ ] Test: curl http://localhost:8000/health

### Day 12: Implement Indicator Endpoints
- [ ] Implement /indicators/{symbol} GET endpoint
  - [ ] Calls engine.get_snapshot()
  - [ ] Returns JSON with all indicator values
  - [ ] Add trading_signal field (BUY/SELL/HOLD based on RSI)
- [ ] Implement /indicators GET endpoint (all symbols)
- [ ] Test with curl

### Day 13: WebSocket Streaming
- [ ] Implement /ws/{symbol} WebSocket endpoint
- [ ] Sends updates every 1 second
- [ ] Test with wscat or JavaScript client
- [ ] Add error handling for invalid symbols

**Deliverable:** Real-time streaming API working

---

## Phase 4: Integration (Days 14-16) ✓

### Day 14: Connect Components
- [ ] Modify binance_consumer callback to call update_engine_with_trade()
- [ ] Implement update_engine_with_trade() in api_server.py
- [ ] Create main.py that runs both consumer and API server
- [ ] Start system: python main.py
- [ ] Verify: API endpoint returns live indicator values

### Day 15: Monitor Data Flow
- [ ] Add throughput metrics to main.py
  - [ ] Count trades per second
  - [ ] Print every 10 seconds
- [ ] Expected: 100-150 trades/sec for 4 symbols
- [ ] Add logging: which symbols active, connection status
- [ ] Test with 1 symbol (should see ~25 trades/sec)

### Day 16: Error Handling & Recovery
- [ ] Test: kill C++ process, verify graceful failure
- [ ] Test: kill Binance connection, verify auto-reconnect
- [ ] Test: invalid JSON from Binance, verify no crash
- [ ] Add comprehensive try/except blocks
- [ ] Log all errors with timestamps

**Deliverable:** System is resilient to failures

---

## Phase 5: Persistence (Days 17-18) ✓

### Day 17: Database Setup
- [ ] Implement IndicatorDatabase class
- [ ] Create SQLite schema (indicators table with indexes)
- [ ] Implement save_indicator() method (async-safe)
- [ ] Implement get_historical_data() method
- [ ] Test: Save 100 indicators, retrieve them

### Day 18: Database Integration
- [ ] Integrate database into API server
- [ ] Add /history/{symbol}?limit=100 endpoint
- [ ] Modify callback to save to DB
- [ ] Query historical data from API

**Deliverable:** Historical data available via API

---

## Phase 6: Testing & Documentation (Days 19-21) ✓

### Day 19: Unit Tests
- [ ] Write tests in tests/test_indicators.py
  - [ ] Test SMA with known inputs
  - [ ] Test RSI in pure uptrend/downtrend
  - [ ] Test concurrent access
- [ ] Run: pytest tests/ -v
- [ ] All tests pass

### Day 20: Integration Tests
- [ ] Write tests/integration_test.py
  - [ ] Start consumer + API + database
  - [ ] Run for 10 seconds
  - [ ] Verify API returns non-empty data
  - [ ] Verify database has entries
- [ ] Run: pytest tests/integration_test.py

### Day 21: Documentation & Polish
- [ ] Write README.md
  - [ ] 1-paragraph description
  - [ ] Architecture diagram (ASCII ok)
  - [ ] How to build & run
  - [ ] API documentation
  - [ ] Performance metrics
- [ ] Create requirements.txt
- [ ] Create ARCHITECTURE.md
- [ ] Add code comments
- [ ] Prepare interview talking points

**Deliverable:** Project is presentation-ready

---

## FINAL DEPLOYMENT CHECKLIST

Before showing to interviewers:

### Code Quality
- [ ] No hardcoded values (use config)
- [ ] Meaningful variable names
- [ ] Comments on complex algorithms
- [ ] Helpful error messages

### Performance
- [ ] REST API response time < 100ms
- [ ] C++ calculation time < 1ms
- [ ] No memory leaks

### Reliability
- [ ] 5-minute continuous run with no errors
- [ ] Graceful error handling demonstrated
- [ ] Proper logging with timestamps

### Documentation
- [ ] README has clear build instructions
- [ ] API is fully documented
- [ ] Architecture diagram is clear
- [ ] Can explain each component in 30 seconds

### Demonstration
- [ ] Can start system with single command
- [ ] Can show live data via curl
- [ ] Can explain technology choices
- [ ] Can answer "How would you scale to 100×?"

---

## REQUIREMENTS.TXT TEMPLATE

```
# Web Framework
fastapi==0.104.1
uvicorn==0.24.0

# WebSocket & Async
websockets==12.0
aiohttp==3.9.1

# Data Processing
asyncio==3.4.3
python-dateutil==2.8.2

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9  # PostgreSQL driver (optional)

# C++ Bindings
pybind11==2.6.2
zmq==0.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1

# Development
black==23.12.0
pylint==3.0.3
```

---

## QUICK DEBUGGING GUIDE

| Problem | Solution |
|---------|----------|
| WebSocket won't connect | Check internet, verify Binance server up, check firewall |
| C++ compile error | Install pybind11: pip install pybind11 |
| No trades showing up | Check symbol format (lowercase: btcusdt, not BTCUSDT) |
| API timeout | Increase engine window size, check C++ performance |
| Database locked error | Close other connections, use WAL mode |
| Memory growing unbounded | Verify old trades removed from deque |
| Port 8000 already in use | Kill existing process or use different port |

---

## TIME BUDGET SUMMARY

| Phase | Days | Hours/Day | Total Hours |
|-------|------|----------|------------|
| Prep | 2 | 1-2 | 3 |
| Python Ingestion | 3 | 3-4 | 10 |
| C++ Engine | 5 | 4-5 | 22 |
| REST API | 3 | 3-4 | 10 |
| Integration | 3 | 2-3 | 8 |
| Persistence | 2 | 2-3 | 5 |
| Testing & Docs | 3 | 2-3 | 8 |
| **TOTAL** | **21** | **2-4 avg** | **66** |

**Total: ~66 hours across 21 days = 3-4 hours/day average**

**If you have less time:** Skip days 17-18 (skip database), still have a great project (12 days, 44 hours).

---

## INTERVIEW TALKING POINTS (Practice These!)

### System Design (2 min)
"I chose an event-driven architecture with three layers: Python ingestion (handles WebSocket), C++ processing (calculates indicators), and Python API (serves results). This separation allows independent scaling—add more Python API servers without recompiling C++."

### Performance (2 min)
"The C++ engine maintains a 500-trade circular buffer. All indicator calculations are O(n) where n ≤ 500, resulting in microsecond latency. Python's JSON parsing alone would be 100× slower, so I use C++ for the hot path."

### Concurrency (1 min)
"I use std::mutex for thread-safe access to the price window without locking the entire calculation. Python's async/await handles multiple symbol streams concurrently—different paradigm but both efficient."

### Real-World Thinking (1 min)
"I implemented exponential backoff for WebSocket reconnects, transaction handling for data integrity, and throughput metrics for observability. These aren't required but are essential in production."

### Scalability (1 min)
"Currently handles 1000+ trades/sec on one machine. To scale 100×, I'd add Kafka between ingestion and processing, run multiple C++ worker processes, and use consistent hashing for symbol-to-worker routing."

---

## GOOD LUCK! 🚀

You've got this. The project is ambitious but achievable in 3 weeks. Start with Phase 0 and work through systematically. Document as you go.

**Pro tips:**
1. Test each component independently before integrating
2. Commit to git frequently
3. Take screenshots of working system
4. Practice your pitch out loud before the interview
5. Be honest about trade-offs and limitations

Let me know if you get stuck!
