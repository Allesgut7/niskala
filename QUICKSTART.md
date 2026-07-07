![NISKALA](Logo-fix.png)

# Niskala - Quick Start Guide

## Overview

**Niskala** is a terminal-based trading dashboard for Indonesian stocks (IDX), featuring:
- Real-time market data (IHSG, IDX stocks, global indices)
- Fear & Greed Index (Indonesia/Asia/Global)
- AI-powered news sentiment analysis (FinBERT)
- Multi-screen TUI with F-key navigation
- WebSocket + polling data streams
- 10-stock watchlist with live updates

Built with: **C++20**, **FTXUI**, **Python 3.10+**, **pybind11**

---

## Installation

### Prerequisites

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y cmake g++ python3 python3-pip python3-venv
sudo apt install -y libsqlite3-dev ninja-build git
```

**macOS:**
```bash
brew install cmake python sqlite ninja git
```

### Build

```bash
cd /home/chalderaaa/findxstation/niskala/
./verify.sh      # Check project integrity
./setup.sh       # Build everything
```

This will:
1. Create Python venv in `.venv/`
2. Install Python deps (yfinance, transformers, torch, etc.)
3. Fetch FTXUI, nlohmann/json, cpp-httplib via CMake
4. Build C++ app to `build/niskala`

Build time: ~3-5 minutes (first run, downloads dependencies)

---

## Run

```bash
./build/niskala
```

**With custom config:**
```bash
./build/niskala --config config/default.json
```

**Help:**
```bash
./build/niskala --help
```

---

## Keyboard Shortcuts

| Key | Screen |
|-----|--------|
| `F1` | Dashboard (main view) |
| `F2` | Market Overview |
| `F3` | Chart |
| `F4` | Screener |
| `F5` | Portfolio |
| `F6` | News Feed |
| `F7` | Settings |
| `q` | Quit |

**Navigation:**
- `↑` `↓` - Navigate lists/tables
- `Enter` - Select/confirm
- `Tab` - Switch panels

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│ IHSG: 7,250 ▲1.2%  │  S&P: 5,450 ▲0.5%  │  Nikkei: 38,500 ▲ │  Top Banner
├─────────────────────────────────────────────────────────────┤
│ 🔴 GOTO +12.5%  │  EMTK -5.2%  │  BBCA +2.1%  │  ...        │  Running Ticker
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Indonesia    │  │ Asia         │  │ Global       │      │  Fear & Greed
│  │  68 GREED    │  │  56 GREED    │  │  71 GREED    │      │  (3 regions)
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌────────────────────────────┐  ┌──────────────────────┐  │
│  │ SYMBOL  PRICE   CHG%  VOL  │  │ NEWS FEED            │  │
│  │ BBCA    9,100   +0.5  1.2M │  │ 10:30 CNBC Bank ▲78  │  │
│  │ BBRI    4,850   +1.2  2.1M │  │ 10:28 IDX Mining +45 │  │  Main Content
│  │ BMRI    6,200   -0.3  1.5M │  │ 10:25 Kontan Tech -12│  │
│  │ ...                        │  │ ...                  │  │
│  └────────────────────────────┘  └──────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Sector Heatmap: Banking ▲ Mining ▲ Tech ▼          │    │  Sector View
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│ F1:Dashboard F2:Market F3:Chart F6:News q:Quit              │  Status Bar
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Watchlist (`config/default.json`)

```json
{
  "watchlist": [
    "BBCA", "BBRI", "BMRI", "TLKM", "GOTO",
    "ADRO", "UNVR", "ICBP", "ASII", "PGAS"
  ],
  "refresh_interval": 30,
  "theme": "dark"
}
```

### Sector Mapping (`config/sector_mapping.json`)

Maps stocks to sectors (FINANCE, MINE, TECH, etc.) and defines IDX30 constituents.

---

## Testing

**Run all tests:**
```bash
source .venv/bin/activate
pytest tests/ -v
```

**Quick tests only (skip slow network tests):**
```bash
pytest tests/ -v -m "not slow"
```

**Specific test file:**
```bash
pytest tests/unit/test_yfinance.py -v
```

---

## Development

### Project Structure

```
niskala/
├── CMakeLists.txt          # C++ build config
├── requirements.txt        # Python deps
├── setup.sh                # Build script
├── verify.sh               # Project integrity check
├── config/                 # JSON configs
│   ├── default.json
│   └── sector_mapping.json
├── src/                    # C++ source
│   ├── main.cpp
│   ├── core/               # Business logic
│   │   ├── common/         # Config, Logger, Types, Utils
│   │   ├── market_data/    # DataAggregator, YFinance, Akshare
│   │   ├── ai/             # Sentiment, News, LLM
│   │   ├── fear_greed/     # Fear & Greed calculator
│   │   └── quant/          # Backtest, Factors, Portfolio (stubs)
│   └── tui/                # FTXUI interface
│       ├── app.cpp         # Main app loop
│       ├── screens/        # 7 screens (Dashboard, Market, Chart, etc.)
│       └── widgets/        # 12 widgets (StockTable, NewsFeed, etc.)
├── python/                 # Python modules
│   ├── data_sources/       # YFinance, Akshare, IDX BEI
│   ├── ai/                 # FinBERT, LLM, News scraper
│   ├── fear_greed/         # Fear & Greed calculator
│   └── utils/              # WebSocket stream
├── tests/                  # Pytest tests
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
└── data/                   # Runtime data
    ├── cache/              # Market data cache
    ├── local_db/           # SQLite DB
    └── niskala.log         # App log
```

### Adding a New Screen

1. Create `src/tui/screens/my_screen.h` and `.cpp`
2. Inherit from `ScreenBase` in `screen_interface.h`
3. Implement `render()`, `on_event()`, `refresh()`, `name()`
4. Add to `app.h` and `app.cpp`
5. Map to F-key in `app.cpp` event handler
6. Add to `CMakeLists.txt`

### Adding a New Widget

1. Create `src/tui/widgets/my_widget.h` and `.cpp`
2. Add `render()` method returning `ftxui::Element`
3. Include in parent screen
4. Add to `CMakeLists.txt`

---

## Logs

Application logs are written to `data/niskala.log`.

**View live logs:**
```bash
tail -f data/niskala.log
```

---

## Known Issues / TODO

- FinBERT model auto-download on first run (~500MB)
- WebSocket not implemented (using polling fallback)
- Chart screen placeholder (Phase 2)
- Screener screen placeholder (Phase 2)
- Quant modules stubbed (Phase 2)

---

## Support

- GitHub: https://github.com/anomalyco/opencode
- Docs: Planning docs in project root (01-23)

---

## License

See project documentation.
