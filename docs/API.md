# API Documentation

## Overview

The Market Data Engine exposes a REST API and WebSocket endpoints for accessing real-time and historical cryptocurrency market indicators.

**Base URL**: `http://localhost:8000` (development)

**API Version**: v1 (implicit, future versions will use `/v2/` prefix)

---

## Authentication

Currently, no authentication is required as this is a read-only API consuming public Binance data.

**Future**: JWT-based authentication for production deployments.

---

## REST Endpoints

### Health Check

**GET** `/health`

Check if the service is running and get basic status information.

**Response**: 200 OK
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600.5,
  "active_symbols": 5
}
```

**Response Fields**:
- `status` (string): Service status (`healthy`, `degraded`, `unhealthy`)
- `version` (string): Application version
- `uptime_seconds` (float): Time since service start
- `active_symbols` (int): Number of symbols being tracked

---

### Get Indicators for Single Symbol

**GET** `/indicators/{symbol}`

Retrieve current technical indicators for a specific trading pair.

**Path Parameters**:
- `symbol` (string, required): Trading pair symbol (e.g., `BTCUSDT`)

**Response**: 200 OK
```json
{
  "symbol": "BTCUSDT",
  "timestamp": "2026-01-16T10:30:00.123456Z",
  "last_price": 45123.50,
  "sma": 45000.25,
  "ema": 45050.75,
  "rsi": 62.5,
  "macd": 125.50,
  "macd_signal": 115.25,
  "macd_histogram": 10.25,
  "trade_count": 487
}
```

**Response Fields**:
- `symbol` (string): Trading pair
- `timestamp` (datetime): When snapshot was taken (ISO 8601)
- `last_price` (float): Most recent trade price
- `sma` (float|null): Simple Moving Average (20-period default)
- `ema` (float|null): Exponential Moving Average (12-period default)
- `rsi` (float|null): Relative Strength Index (0-100 scale, 14-period default)
- `macd` (float|null): MACD line value
- `macd_signal` (float|null): MACD signal line (9-period EMA of MACD)
- `macd_histogram` (float|null): MACD histogram (MACD - Signal)
- `trade_count` (int): Number of trades in calculation window

**Note**: Indicator values are `null` if insufficient data is available (e.g., fewer than 20 trades for SMA-20).

**Error Responses**:

404 Not Found - Symbol not tracked
```json
{
  "detail": "Symbol XYZUSDT is not being tracked"
}
```

---

### Get Indicators for All Symbols

**GET** `/indicators`

Retrieve current indicators for all tracked symbols.

**Response**: 200 OK
```json
[
  {
    "symbol": "BTCUSDT",
    "timestamp": "2026-01-16T10:30:00Z",
    "last_price": 45123.50,
    "sma": 45000.25,
    ...
  },
  {
    "symbol": "ETHUSDT",
    "timestamp": "2026-01-16T10:30:01Z",
    "last_price": 2345.75,
    "sma": 2340.10,
    ...
  }
]
```

**Response**: Array of `IndicatorSnapshot` objects (same structure as single-symbol endpoint)

---

### Get Historical Indicators

**GET** `/history/{symbol}`

Retrieve historical indicator snapshots for a specific symbol.

**Path Parameters**:
- `symbol` (string, required): Trading pair symbol

**Query Parameters**:
- `start_time` (datetime, optional): Start of time range (ISO 8601, default: 24 hours ago)
- `end_time` (datetime, optional): End of time range (ISO 8601, default: now)
- `limit` (int, optional): Max number of results (default: 100, max: 1000)
- `offset` (int, optional): Pagination offset (default: 0)

**Example Request**:
```
GET /history/BTCUSDT?start_time=2026-01-15T00:00:00Z&end_time=2026-01-16T00:00:00Z&limit=50
```

**Response**: 200 OK
```json
{
  "symbol": "BTCUSDT",
  "count": 50,
  "snapshots": [
    {
      "timestamp": "2026-01-15T00:01:00Z",
      "last_price": 44500.00,
      "sma": 44480.50,
      ...
    },
    ...
  ]
}
```

**Response Fields**:
- `symbol` (string): Trading pair
- `count` (int): Number of snapshots returned
- `snapshots` (array): Array of historical `IndicatorSnapshot` objects

---

### Get Trading Signal

**GET** `/signal/{symbol}`

Get a simple trading signal based on current indicators.

**Path Parameters**:
- `symbol` (string, required): Trading pair symbol

**Response**: 200 OK
```json
{
  "symbol": "BTCUSDT",
  "signal": "BUY",
  "confidence": 0.75,
  "reason": "RSI below 30 indicates oversold condition",
  "timestamp": "2026-01-16T10:30:00Z"
}
```

**Response Fields**:
- `symbol` (string): Trading pair
- `signal` (string): `BUY`, `SELL`, or `HOLD`
- `confidence` (float): Signal strength (0.0 to 1.0)
- `reason` (string): Human-readable explanation
- `timestamp` (datetime): When signal was generated

**Signal Rules** (current implementation):
- **BUY**: RSI < 30 (oversold)
- **SELL**: RSI > 70 (overbought)
- **HOLD**: 30 ≤ RSI ≤ 70 (neutral)

**Note**: These are simple educational signals, not financial advice.

---

## WebSocket Endpoints

### Real-Time Indicator Stream

**WS** `/ws/{symbol}`

Subscribe to real-time indicator updates for a specific symbol.

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/BTCUSDT');

ws.onopen = () => {
  console.log('Connected to BTCUSDT stream');
};

ws.onmessage = (event) => {
  const snapshot = JSON.parse(event.data);
  console.log('Indicator update:', snapshot);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from stream');
};
```

**Message Format**: Same as `IndicatorSnapshot` from REST endpoints

**Update Frequency**: ~1 second (configurable)

**Connection Limits**: Max 100 concurrent connections per symbol (future implementation)

---

## Error Responses

All endpoints follow consistent error response format:

**400 Bad Request**:
```json
{
  "detail": "Invalid symbol format. Expected format: BTCUSDT"
}
```

**404 Not Found**:
```json
{
  "detail": "Symbol XYZUSDT is not being tracked"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error",
  "error_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**503 Service Unavailable**:
```json
{
  "detail": "Service is starting up, please try again in a few seconds"
}
```

---

## Rate Limiting

**Current**: No rate limiting

**Future Implementation**:
- **REST**: 100 requests per minute per IP
- **WebSocket**: 10 connections per IP
- Response header: `X-RateLimit-Remaining: 95`
- 429 Too Many Requests response when exceeded

---

## CORS

CORS is enabled for development with permissive settings:
- **Allowed Origins**: `*` (all)
- **Allowed Methods**: GET, POST, OPTIONS
- **Allowed Headers**: `*`

**Production**: Configure specific origins in `.env`

---

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Example Client Usage

### Python

```python
import httpx
import asyncio

async def get_indicators():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/indicators/BTCUSDT")
        print(response.json())

asyncio.run(get_indicators())
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

async function getIndicators() {
  const response = await axios.get('http://localhost:8000/indicators/BTCUSDT');
  console.log(response.data);
}

getIndicators();
```

### cURL

```bash
# Get single symbol indicators
curl http://localhost:8000/indicators/BTCUSDT

# Get all symbols
curl http://localhost:8000/indicators

# Get historical data
curl "http://localhost:8000/history/BTCUSDT?limit=10"

# WebSocket connection (using websocat)
websocat ws://localhost:8000/ws/BTCUSDT
```

---

## Performance Expectations

| Endpoint | Typical Latency | Max Throughput |
|----------|----------------|----------------|
| `/health` | <5ms | 1000+ req/sec |
| `/indicators/{symbol}` | <20ms | 500+ req/sec |
| `/indicators` (all) | <50ms | 200+ req/sec |
| `/history/{symbol}` | <100ms | 100+ req/sec |
| WebSocket broadcast | <50ms | 100+ concurrent clients |

**Note**: Performance degrades with higher symbol counts and longer historical queries.

---

## Future Enhancements

- [ ] GraphQL endpoint for flexible queries
- [ ] Server-Sent Events (SSE) as WebSocket alternative
- [ ] Batch indicator requests (`POST /indicators/batch`)
- [ ] Custom indicator parameters (e.g., `/indicators/BTCUSDT?rsi_period=21`)
- [ ] Data export endpoints (CSV, JSON)
- [ ] Alerting webhooks (trigger when RSI crosses threshold)
