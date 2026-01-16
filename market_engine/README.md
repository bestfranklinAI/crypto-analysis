# Market Engine C++ Module

This directory contains the high-performance C++ core for technical indicator calculations.

## Building the Module

### Prerequisites
- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)
- CMake 3.18+
- Python 3.13+
- pybind11 (installed via pip)

### Build Instructions

#### Linux/macOS
```bash
cd market_engine
mkdir build
cd build
cmake ..
make
```

#### Windows
```bash
cd market_engine
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

### Install to Python Environment
```bash
# From build directory
cmake --install . --prefix ../..
```

Or copy the compiled module:
```bash
# Linux
cp market_engine.so ../../

# macOS
cp market_engine.so ../../

# Windows
cp Release/market_engine.pyd ../../
```

## Testing the Module
```python
import market_engine

# Create engine instance
engine = market_engine.MarketIndicatorEngine(max_window_size=500)

# Add a trade
trade = market_engine.Trade(
    price=45123.50,
    volume=0.15,
    timestamp=1705401600000,
    symbol="BTCUSDT"
)
engine.add_trade(trade)

# Get indicators
snapshot = engine.get_snapshot()
print(f"SMA: {snapshot.sma}")
print(f"RSI: {snapshot.rsi}")
```

## Performance Notes
- Target: <1ms per indicator calculation
- Optimized for 500-trade sliding windows
- Thread-safe with minimal locking overhead
- Zero-copy where possible
