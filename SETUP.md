# Setup Guide

## Quick Setup (5 minutes)

### 1. System Requirements Check

```bash
# Verify Python version (must be 3.13+)
python3 --version

# Verify C++ compiler
g++ --version  # Linux/macOS
# or
clang --version  # macOS
# or
cl  # Windows (MSVC)

# Verify CMake
cmake --version
```

### 2. Clone and Navigate

```bash
git clone https://github.com/yourusername/market-data-engine.git
cd market-data-engine
```

### 3. Python Environment

```bash
# Create virtual environment
python3.13 -m venv venv

# Activate (choose your platform)
source venv/bin/activate              # Linux/macOS
venv\Scripts\activate                 # Windows CMD
venv\Scripts\Activate.ps1            # Windows PowerShell

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 4. Build C++ Module

**Linux/macOS:**
```bash
cd market_engine
mkdir build && cd build
cmake ..
make -j$(nproc)  # Parallel build
cd ../..

# Copy module to project root
cp market_engine/build/market_engine*.so .
```

**Windows:**
```bash
cd market_engine
mkdir build && cd build
cmake ..
cmake --build . --config Release
cd ..\..

# Copy module to project root
copy market_engine\build\Release\market_engine.pyd .
```

### 5. Verify C++ Module

```bash
python -c "import market_engine; print('✓ C++ module loaded successfully')"
```

If this works, you're good to go! 🎉

### 6. Configure Environment

```bash
cp .env.example .env

# Optional: Edit .env to change symbols or settings
nano .env  # or use your favorite editor
```

### 7. Run the Application

```bash
python main.py
```

**Expected output:**
```
Starting Market Data Engine v0.1.0...
INFO: Connecting to Binance WebSocket...
INFO: Connected to Binance for symbols: BTCUSDT, ETHUSDT
INFO: FastAPI server running on http://0.0.0.0:8000
```

### 8. Test the API

Open browser: **http://localhost:8000/docs**

Or use curl:
```bash
# Health check
curl http://localhost:8000/health

# Get indicators
curl http://localhost:8000/indicators/BTCUSDT
```

---

## Troubleshooting

### Issue: "No module named 'pybind11'"

**Solution:**
```bash
pip install pybind11
```

### Issue: "CMake not found"

**Solution:**
```bash
# macOS
brew install cmake

# Ubuntu/Debian
sudo apt-get install cmake

# Windows
# Download from: https://cmake.org/download/
```

### Issue: "C++ compiler not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install

# Windows
# Install Visual Studio Build Tools:
# https://visualstudio.microsoft.com/downloads/
```

### Issue: "ImportError: No module named 'market_engine'"

**Solution:**
Make sure the compiled `.so` or `.pyd` file is in the project root:
```bash
ls -la market_engine*.so   # Linux/macOS
dir market_engine.pyd       # Windows
```

If missing, copy it from `market_engine/build/`:
```bash
cp market_engine/build/market_engine*.so .   # Linux/macOS
copy market_engine\build\Release\market_engine.pyd .  # Windows
```

### Issue: "Port 8000 already in use"

**Solution:**
Change the port in `.env`:
```ini
API_PORT=8080
```

Or kill the process using port 8000:
```bash
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Development Workflow

### 1. Start Development Server

```bash
# With auto-reload (useful during development)
uvicorn app.api_server:app --reload --port 8000
```

### 2. Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

### 3. Code Formatting

```bash
# Format Python code
black app/ tests/

# Lint Python code
ruff check app/ tests/

# Type checking
mypy app/
```

### 4. Rebuild C++ Module (after changes)

```bash
cd market_engine/build
make -j$(nproc)
cp market_engine*.so ../..
cd ../..
```

---

## Next Steps

1. **Read the documentation**: Start with [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. **Explore the API**: Open http://localhost:8000/docs
3. **Run tests**: `pytest tests/`
4. **Follow the roadmap**: See [Project Management/roadmap.md](Project%20Management/roadmap.md)
5. **Start coding**: Begin with Phase 1 tasks in the checklist

---

## Getting Help

- **Documentation**: Check [docs/](docs/) folder
- **GitHub Issues**: Report bugs or ask questions
- **Project Management**: See [checklist.md](Project%20Management/checklist.md) for development tasks

---

Happy coding! 🚀
