![NISKALA](Logo-fix.png)

# Niskala - Complete Project README

**Version:** 1.0.0  
**Status:** Production Ready  
**Date:** July 3, 2026

---

## 🚀 Overview

**Niskala** is a professional-grade Indonesian stock market terminal featuring AI-powered sentiment analysis, quantitative trading tools, and real-time collaboration. Built with C++ (terminal UI) and Python (AI/quant modules).

### Key Features

✅ **AI Sentiment Analysis**
- FinBERT + LLM (GPT-4/Claude) interpretation
- Multi-source news scraping (6 sources)
- Sector/emiten impact mapping
- Real-time sentiment scoring (-100 to +100)

✅ **Quantitative Trading Lab**
- Event-driven backtesting (IDX commission model)
- Multi-factor analysis (Value, Momentum, Quality, Size)
- Portfolio optimization (Mean-Variance, HRP, Black-Litterman)
- Risk metrics (VaR, CVaR, Sharpe, Sortino, Max DD)
- DCF valuation with Monte Carlo simulation

✅ **Advanced Analytics**
- Stock screener (80+ filters, 8 presets)
- Pattern recognition (15 patterns)
- Correlation analysis & clustering
- ASCII chart engine (candlestick, multi-timeframe)
- Order book & trade visualization

✅ **Collaboration & Bots**
- Shared watchlists (real-time sync)
- Telegram bot (8 commands)
- Discord bot (6 slash commands)
- Price alerts & notifications

✅ **Production Ready**
- Docker deployment
- CI/CD with GitHub Actions
- Multi-platform builds (Linux, macOS)
- Performance optimized (< 50MB memory)

---

## 📊 Project Stats

| Metric | Count |
|--------|-------|
| **Total Files** | 115+ |
| **Total LOC** | ~23,700 |
| **Python Files** | 38 |
| **Python LOC** | ~8,700 |
| **C++ Files** | 77 |
| **Test Files** | 11 |
| **Packages** | 8 |

---

## 🏗️ Architecture

```
niskala/
├── src/                   # C++ terminal UI (77 files, ~15,000 LOC)
│   ├── core/             # Core logic, data structures
│   ├── ui/               # FTXUI components
│   └── utils/            # Utilities
│
├── python/               # Python modules (38 files, ~8,700 LOC)
│   ├── ai/               # Sentiment pipeline (5 files, 854 LOC)
│   ├── analytics/        # Charts, screener, patterns (7 files, 2,000+ LOC)
│   ├── collaboration/    # Shared watchlists (2 files, 615 LOC)
│   ├── data_sources/     # Market data (4 files, 509 LOC)
│   ├── fear_greed/       # F&G index (3 files, 646 LOC)
│   ├── integrations/     # Telegram, Discord (3 files, 606 LOC)
│   ├── quant/            # Backtest, portfolio, risk (7 files, 2,205 LOC)
│   └── utils/            # Cache, WebSocket (3 files, 542 LOC)
│
├── tests/                # Unit tests (11 files)
├── data/                 # Local database & cache
├── models/               # AI models (FinBERT)
└── docs/                 # Documentation (20+ MD files)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **C++ compiler** (GCC 11+, Clang 14+, MSVC 2022)
- **CMake 3.20+**
- **Docker** (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/niskala.git
cd niskala

# Install Python dependencies
pip install -r requirements.txt

# Build C++ terminal
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build

# Run
./build/niskala
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f niskala

# Stop
docker-compose down
```

---

## 📦 Python Modules

### AI Sentiment Pipeline

```python
from ai import SentimentPipeline, LLMInterpreter

# Initialize pipeline
pipeline = SentimentPipeline(use_llm=True, llm_provider='openai')

# Analyze news
result = pipeline.analyze("BBRI Q3 laba naik 15% YoY")
print(f"Score: {result.sentiment_score}")  # -100 to +100
print(f"Sectors: {result.sectors}")
print(f"Impact: {result.impact}")
```

### Quant Lab

```python
from quant import BacktestEngine, PortfolioOptimizer, RiskCalculator

# Backtest strategy
engine = BacktestEngine(initial_capital=100_000_000)
engine.add_strategy(MACrossoverStrategy())
results = engine.run(data)

# Optimize portfolio
optimizer = PortfolioOptimizer()
result = optimizer.optimize_mean_variance(returns)

# Calculate risk
calculator = RiskCalculator()
metrics = calculator.calculate(returns, benchmark)
```

### Analytics

```python
from analytics import ASCIIChart, AdvancedScreener, PatternDetector

# Render chart
chart = ASCIIChart()
print(chart.render_candlestick(df, title="BBRI"))

# Screen stocks
screener = AdvancedScreener()
results = screener.screen(stocks, preset='value')

# Detect patterns
detector = PatternDetector()
patterns = detector.detect(df)
```

### Integrations

```python
from integrations import NiskalaTelegramBot, NiskalaDiscordBot

# Telegram bot
telegram_bot = NiskalaTelegramBot(token=TELEGRAM_TOKEN)
telegram_bot.run()

# Discord bot
discord_bot = NiskalaDiscordBot(token=DISCORD_TOKEN)
discord_bot.run()
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=python --cov-report=html

# Run specific phase
pytest tests/unit/test_phase2_quant.py -v
pytest tests/unit/test_phase3_charts.py -v
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `README.md` | This file |
| `PHASE2_SUMMARY.md` | AI & Quant Lab implementation |
| `PHASE3_SUMMARY.md` | Charts & Deployment implementation |
| `03_DASHBOARD_LAYOUT.md` | Dashboard UI design |
| `08_STOCK_DETAIL.md` | Stock detail screen spec |
| `09_DEVELOPMENT_PHASES.md` | Development roadmap |
| `13_ENHANCED_FEATURES.md` | Enhanced features guide |
| `20_DEPLOYMENT.md` | Deployment guide |

---

## 🎯 Features by Phase

### Phase 1: Core Terminal (Completed)
- ✅ TUI with FTXUI
- ✅ Stock table & watchlist
- ✅ Basic charts
- ✅ Market data integration

### Phase 2: AI & Quant Lab (Completed)
- ✅ AI sentiment pipeline (FinBERT + LLM)
- ✅ News scraping (6 sources)
- ✅ Backtesting engine
- ✅ Factor analysis
- ✅ Portfolio optimizer
- ✅ Risk metrics
- ✅ Signal generator
- ✅ DCF model
- ✅ Advanced screener
- ✅ Pattern recognition
- ✅ Correlation analysis
- ✅ Shared watchlists
- ✅ Telegram bot

### Phase 3: Charts & Deploy (Completed)
- ✅ ASCII chart engine
- ✅ Multi-timeframe support
- ✅ Technical indicators
- ✅ Stock detail screen (6 tabs)
- ✅ Order book visualization
- ✅ Discord bot
- ✅ Docker deployment
- ✅ CI/CD pipeline

---

## 🔧 Configuration

### Environment Variables

```bash
# API Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export TELEGRAM_TOKEN="123456789:ABC..."
export DISCORD_TOKEN="MTIzNDU2Nzg5..."

# Data Sources
export YAHOO_FINANCE_ENABLED=true
export IDX_API_ENABLED=true

# Cache
export CACHE_TTL=300
export CACHE_MAX_SIZE=1000

# Logging
export LOG_LEVEL=INFO
```

### Config File

```json
{
  "api_keys": {
    "openai": "sk-...",
    "anthropic": "sk-ant-..."
  },
  "data_sources": {
    "yahoo_finance": true,
    "idx_api": true
  },
  "cache": {
    "ttl": 300,
    "max_size": 1000
  },
  "logging": {
    "level": "INFO",
    "file": "data/logs/niskala.log"
  }
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **FTXUI** - Terminal UI framework
- **Transformers** - FinBERT models
- **TA-Lib** - Technical analysis
- **yfinance** - Market data
- **Discord.py** - Discord bot framework
- **python-telegram-bot** - Telegram bot framework

---

## 📞 Contact

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

**Made with ❤️ for Indonesian traders**

*Last updated: July 3, 2026*
