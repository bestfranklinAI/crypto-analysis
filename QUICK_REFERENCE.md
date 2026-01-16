# Quick Reference Guide

## 🚀 Common Commands

### Development

```bash
# Setup
python3.13 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Build C++ module
cd market_engine && mkdir build && cd build
cmake .. && make
cp market_engine*.so ../..

# Run application
python main.py

# Run with auto-reload (development)
uvicorn app.api_server:app --reload
```

### Testing

```bash
# All tests
pytest

# Specific test file
pytest tests/test_indicators.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v -s
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint
ruff check app/ tests/

# Type check
mypy app/

# All checks at once
black . && ruff check . && mypy app/
```

### Docker

```bash
# Build
docker build -t market-data-engine .

# Run
docker run -d -p 8000:8000 --name market-engine market-data-engine

# Logs
docker logs -f market-engine

# Stop
docker stop market-engine && docker rm market-engine

# Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## 📁 File Locations

| Need to... | Go to... |
|------------|----------|
| Configure app | `.env` or `app/config.py` |
| Add API endpoint | `app/api_server.py` |
| Change indicators | `market_engine/indicators.cpp` |
| Add Pydantic model | `app/schemas/indicators.py` |
| Database operations | `app/database.py` |
| WebSocket consumer | `app/binance_consumer.py` |
| Orchestration logic | `app/services/orchestration.py` |
| Tests | `tests/test_*.py` |
| Documentation | `docs/*.md` |

---

## 🔧 Configuration Quick Edit

```ini
# .env file - most commonly changed settings

# Symbols to track (add/remove as needed)
SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,ADAUSDT,SOLUSDT

# API port (change if 8000 is in use)
API_PORT=8000

# Logging (DEBUG for development, WARNING for production)
LOG_LEVEL=INFO

# Trade window size (affects memory usage)
MAX_TRADE_WINDOW=500

# Indicator periods (adjust for different strategies)
SMA_PERIOD=20
EMA_PERIOD=12
RSI_PERIOD=14
```

---

## 🐛 Debugging Checklist

Problem: **Can't import market_engine**
- [ ] Built C++ module? (`cd market_engine/build && make`)
- [ ] Copied .so/.pyd to root? (`cp market_engine*.so .`)
- [ ] In correct venv? (`which python`)

Problem: **WebSocket connection failed**
- [ ] Internet connection working?
- [ ] Firewall blocking WebSocket?
- [ ] Check `BINANCE_WS_URL` in `.env`

Problem: **Port already in use**
- [ ] Change `API_PORT` in `.env`
- [ ] Or kill process: `lsof -ti:8000 | xargs kill -9`

Problem: **Import errors**
- [ ] Activated venv? (`source venv/bin/activate`)
- [ ] Installed deps? (`pip install -r requirements.txt`)
- [ ] In project root? (`ls main.py`)

---

## 📊 API Testing Commands

```bash
# Health check
curl http://localhost:8000/health

# Get indicators for BTCUSDT
curl http://localhost:8000/indicators/BTCUSDT

# Get all indicators
curl http://localhost:8000/indicators

# Get trading signal
curl http://localhost:8000/signal/BTCUSDT

# Historical data
curl "http://localhost:8000/history/BTCUSDT?limit=10"

# Pretty print JSON
curl http://localhost:8000/indicators/BTCUSDT | jq .

# WebSocket test (using websocat)
websocat ws://localhost:8000/ws/BTCUSDT
```

---

## 🎯 Development Workflow

### Starting a coding session:

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Pull latest changes (if working with team)
git pull

# 3. Check what you need to work on
cat "Project Management/checklist.md"

# 4. Run tests to ensure baseline
pytest

# 5. Start development server
python main.py
```

### Ending a coding session:

```bash
# 1. Format and lint code
black . && ruff check .

# 2. Run tests
pytest

# 3. Commit changes
git add .
git commit -m "feat: implement X"
git push

# 4. Deactivate environment
deactivate
```

---

## 📦 Adding Dependencies

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Install package
pip install package-name

# 3. Update requirements
pip freeze > requirements.txt

# 4. Update pyproject.toml if needed
# (manually add to dependencies list)
```

---

## 🔍 Useful Python Snippets

### Test config loading:
```python
from app.config import settings
print(settings.symbol_list)
print(settings.binance_ws_url)
```

### Test Pydantic models:
```python
from app.schemas.indicators import IndicatorSnapshot
from datetime import datetime

snap = IndicatorSnapshot(
    symbol="BTCUSDT",
    timestamp=datetime.now(),
    last_price=45000.0,
    sma=44500.0,
    ema=44600.0,
    rsi=55.5,
    trade_count=100
)
print(snap.model_dump_json(indent=2))
```

### Test C++ module (after building):
```python
import market_engine

# Create engine
engine = market_engine.MarketIndicatorEngine(500)

# Add trades
trade = market_engine.Trade(45000.0, 1.5, 1705401600000, "BTCUSDT")
engine.add_trade(trade)

# Get snapshot
snapshot = engine.get_snapshot()
print(f"Last price: {snapshot.last_price}")
```

---

## 🎨 VS Code Setup (Optional)

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

---

## 📈 Performance Monitoring

```python
# Add to your code for timing
import time

start = time.perf_counter()
# ... your code ...
duration = time.perf_counter() - start
print(f"Operation took {duration*1000:.2f}ms")
```

---

## 🔗 Important Links

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **pybind11 Docs**: https://pybind11.readthedocs.io
- **Binance API**: https://binance-docs.github.io/apidocs/spot/en/
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html
- **SQLAlchemy**: https://docs.sqlalchemy.org/

---

## 💾 Git Workflow

```bash
# Create feature branch
git checkout -b feature/websocket-consumer

# Make changes, commit frequently
git add app/binance_consumer.py
git commit -m "feat: implement WebSocket consumer"

# Push to remote
git push origin feature/websocket-consumer

# Merge to main (after review)
git checkout main
git merge feature/websocket-consumer
git push origin main
```

---

## 🎓 Learning Resources

**If you're stuck on:**
- Python async → Read FastAPI's async tutorial
- C++ indicators → Look up "trading indicators algorithm"
- WebSockets → Check websockets library docs
- Testing → Read pytest documentation
- Type hints → PEP 484 and mypy docs

---

## ✅ Pre-Deployment Checklist

Before deploying:
- [ ] All tests passing (`pytest`)
- [ ] Code formatted (`black .`)
- [ ] No linting errors (`ruff check .`)
- [ ] Type checks pass (`mypy app/`)
- [ ] Documentation updated
- [ ] `.env` configured for production
- [ ] Database backups configured
- [ ] Monitoring/logging enabled
- [ ] HTTPS configured (production)
- [ ] Error handling tested

---

**Keep this file open in a tab for quick reference while coding!** 📌
