<div align="center">

![NISKALA](Logo-fix.png)

# NISKALA

### Reveal the Unseen

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![C++20](https://img.shields.io/badge/C++-20-00599C.svg?logo=cplusplus&logoColor=white)](https://isocpp.org)
[![Qt6](https://img.shields.io/badge/Qt-6-41CD52.svg?logo=qt&logoColor=white)](https://qt.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)

A professional-grade trading terminal for the Indonesian stock market (IDX)
with AI-powered sentiment analysis, quantitative trading tools, and multi-market support.

</div>

---

## Overview

**Niskala** is a high-performance trading terminal purpose-built for the Indonesian stock market. It combines real-time market data, AI-driven sentiment analysis (FinBERT + LLM), and institutional-grade quantitative tools into a single unified platform.

Built with **Qt6** (desktop GUI), **C++20** (core engine), and **Python** (AI/ML modules), Niskala delivers Bloomberg-level capabilities without the enterprise price tag.

---

## Key Features

<table>
<tr>
<td width="50%">

#### AI-Powered Sentiment Analysis
- FinBERT + LLM (GPT-4 / Claude) interpretation
- Multi-source news scraping from 6+ providers
- Sector & emiten impact mapping
- Real-time sentiment scoring (-100 to +100)

</td>
<td width="50%">

#### Quantitative Trading Lab
- Event-driven backtesting (IDX commission model)
- Multi-factor analysis (Value, Momentum, Quality, Size)
- Portfolio optimization (Mean-Variance, HRP, Black-Litterman)
- Risk metrics (VaR, CVaR, Sharpe, Sortino, Max DD)

</td>
</tr>
<tr>
<td>

#### Advanced Analytics & Screener
- Stock screener with 80+ filters & 8 presets
- Pattern recognition (15 candlestick patterns)
- Correlation analysis & clustering
- Candlestick charts with MA overlays

</td>
<td>

#### Multi-Market & Collaboration
- 6 markets: IDX, SGX, Bursa, SET, PSE, HOSE
- 7 languages (EN, ID, MS, TH, VN, TL, ZH)
- 10 currencies with real-time conversion
- Telegram & Discord bot integrations

</td>
</tr>
</table>

---

## Qt6 Desktop UI

Niskala features a **Bloomberg-style dark theme** built with Qt6:

```
┌─────────────────────────────────────────────────────────────────┐
│  FILE  VIEW  TOOLS  HELP                                        │
├─────────────────────────────────────────────────────────────────┤
│ [SCROLLING TICKER] IHSG, S&P500, Gold, USD/IDR                  │
├─────────────────────────────────────────────────────────────────┤
│ [RUNNING TRADES] BBCA 9200 150K ● BBRI 4800 200K ● ...         │
├──────────────────┬──────────────────────────┬───────────────────┤
│ WATCHLIST (F1)   │ CHART (F2)               │ NEWS (F6)         │
│ BBCA 9200 +1.6%  │ ▲▼▲ Candlestick         │ BBRI ↑ 15%       │
│ BBRI 4800 -1.0%  │  MA5 (yellow)            │ GOTO ↑ 25%       │
│ BMRI 6150 +1.2%  │  MA20 (cyan)             │ ...               │
├──────────────────┤ SCREENER (F3)            ├───────────────────┤
│ FEAR/GREED       │ PORTFOLIO (F4)           │ ORDER BOOK        │
│ [ID] [ASIA] [GL] │ MARKET (F5)              │ 9250: 150        │
├──────────────────┴──────────────────────────┴───────────────────┤
│ GAINERS: ICBP +1.82% ADRO +2.01% │ LOSERS: GOTO -2.30%        │
├─────────────────────────────────────────────────────────────────┤
│ [> Command Bar]  Type: DASH CHART SCREENER PORT HELP            │
├─────────────────────────────────────────────────────────────────┤
│  IHSG: 7,123.45 (+0.50%)    Connected    Niskala v2.0.0        │
└─────────────────────────────────────────────────────────────────┘
```

### Screens

| Screen | Key | Description |
|--------|-----|-------------|
| Dashboard | F1 | Watchlist + Fear/Greed gauges |
| Chart | F2 | Candlestick + MA5/MA20 + timeframes |
| Screener | F3 | Stock filter (search, sector, change, volume) |
| Portfolio | F4 | Open positions, trades, P&L cards |
| Market | F5 | Indices, commodities, forex, gainers/losers |
| News | F6 | Filterable news with sentiment |
| Settings | F7 | Theme, language, data source, shortcuts |

### Widgets

| Widget | Description |
|--------|-------------|
| TopBannerWidget | Scrolling market indices ticker |
| RunningTradeTicker | Live trade scrolling marquee |
| BottomBanner | Gainers vs Losers strip |
| CandlestickChart | OHLC + MA overlays (Qt6 Charts) |
| OrderBookWidget | Bid/Ask depth 8-level |
| FearGreedGauge | Semicircle gauge (ID/ASIA/GLOBAL) |
| SectorHeatmap | 3x3 color-coded sector grid |
| SentimentGauge | Bullish/Bearish/Neutral gauge |
| CommandBar | Command input with history |
| PythonBridge | QProcess bridge to Python modules |

---

## Tech Stack

<div align="center">

![C++20](https://img.shields.io/badge/C++-20-00599C.svg?logo=cplusplus&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)
![Qt6](https://img.shields.io/badge/Qt-6-41CD52.svg?logo=qt&logoColor=white)
![FTXUI](https://img.shields.io/badge/FTXUI-Terminal%20UI-blue)
![Docker](https://img.shields.io/badge/Docker-2496ED.svg?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?logo=githubactions&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192.svg?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D.svg?logo=redis&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi&logoColor=white)

</div>

---

## Getting Started

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| C++ Compiler | GCC 11+ / Clang 14+ / MSVC 2022 |
| CMake | 3.20+ |
| Qt6 | 6.5+ (Core, Gui, Widgets, Charts, Network) |
| Ninja | Latest (optional, for faster builds) |
| Docker | 20.10+ *(optional)* |

### Installation

```bash
# Clone the repository
git clone https://github.com/Allesgut7/niskala.git
cd niskala

# Install Python dependencies
pip install -r requirements.txt

# Build C++ terminal (legacy TUI)
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
./build/niskala
```

### Qt6 Desktop App (Recommended)

```bash
# Build Qt6 desktop app
cd src/ui
mkdir build && cd build
cmake .. -G Ninja
ninja

# Run
./bin/niskala
```

### Docker Deployment

```bash
# Production deployment
docker-compose up -d

# View logs
docker-compose logs -f niskala

# Stop services
docker-compose down
```

---

## Architecture

```
niskala/
├── src/
│   ├── core/                    # C++ core engine (77 files, ~15,000 LOC)
│   │   ├── ai/                  # Sentiment analyzer, LLM client
│   │   ├── fear_greed/          # Multi-region Fear & Greed Index
│   │   ├── market_data/         # Data providers (yfinance, akshare)
│   │   └── quant/               # Backtest, factor, portfolio, risk
│   │
│   ├── tui/                     # Legacy FTXUI terminal (deprecated)
│   │
│   └── ui/                      # Qt6 Desktop App (NEW)
│       ├── app/                 # MainWindow, entry point
│       ├── core/                # PythonBridge, DataManager
│       ├── ui/
│       │   ├── theme/           # Bloomberg dark theme
│       │   ├── widgets/         # 10 custom widgets
│       │   └── screens/         # 7 screens
│       └── resources/           # Icons, fonts, themes
│
├── python/                      # Python modules (38 files, ~8,700 LOC)
│   ├── ai/                      # Sentiment pipeline, NLP, models
│   ├── analytics/               # Screener, patterns, correlation
│   ├── broker/                  # Broker integrations (Ajaib, Stockbit)
│   ├── cloud/                   # Config, cache, database, queue
│   ├── i18n/                    # 7-language translation engine
│   ├── integrations/            # Telegram & Discord bots
│   ├── markets/                 # 6-market config (IDX, SGX, etc.)
│   ├── marketplace/             # Strategy marketplace
│   ├── quant/                   # Backtest, DCF, portfolio, risk
│   ├── social/                  # Copy trading, leaderboard
│   └── trading/                 # Paper engine, order, position
│
├── config/                      # Application configuration
├── tests/                       # Unit & integration tests
├── gcp/                         # Cloud deployment scripts
└── docker-compose.yml           # Container orchestration
```

---

## Project Metrics

| Metric | Value |
|--------|-------|
| Total Files | 57+ |
| Total Lines of Code | ~32,500 |
| C++ Source Files | 77 |
| Python Modules | 38 |
| Qt6 UI Files | 57 |
| Qt6 UI LOC | ~5,500 |
| Test Files | 11 |
| Supported Markets | 6 |
| Supported Languages | 7 |
| Supported Currencies | 10 |

---

## API & Modules

### Sentiment Analysis

```python
from ai import SentimentPipeline

pipeline = SentimentPipeline(use_llm=True, llm_provider="openai")
result = pipeline.analyze("BBRI Q3 laba naik 15% YoY")

print(f"Score: {result.sentiment_score}")   # -100 to +100
print(f"Sectors: {result.sectors}")          # ["banking", "finance"]
print(f"Impact: {result.impact}")            # bullish / bearish / neutral
```

### Quantitative Lab

```python
from quant import BacktestEngine, PortfolioOptimizer, RiskCalculator

# Backtest
engine = BacktestEngine(initial_capital=100_000_000)
results = engine.run(data)

# Portfolio optimization
optimizer = PortfolioOptimizer()
weights = optimizer.optimize_mean_variance(returns)

# Risk metrics
calculator = RiskCalculator()
metrics = calculator.calculate(returns, benchmark)
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=python --cov-report=html

# Run specific module
pytest tests/unit/test_sentiment.py -v
pytest tests/unit/test_fear_greed.py -v
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Getting started guide |
| [CHANGELOG.md](CHANGELOG.md) | Version history & release notes |
| [docs/API.md](docs/API.md) | REST API documentation |
| [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) | Core terminal implementation |
| [PHASE2_SUMMARY.md](PHASE2_SUMMARY.md) | AI & Quant Lab |
| [PHASE3_SUMMARY.md](PHASE3_SUMMARY.md) | Charts & deployment |
| [PHASE4_SUMMARY.md](PHASE4_SUMMARY.md) | Broker integration |
| [PHASE5_SUMMARY.md](PHASE5_SUMMARY.md) | Social & marketplace |
| [PHASE6_SUMMARY.md](PHASE6_SUMMARY.md) | Advanced AI models |
| [PHASE7_SUMMARY.md](PHASE7_SUMMARY.md) | Global expansion |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built for the Indonesian capital market**

[@Allesgut7](https://github.com/Allesgut7)

</div>
