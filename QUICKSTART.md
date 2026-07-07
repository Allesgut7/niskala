![NISKALA](Logo-fix.png)

# Niskala - Quick Start Guide

Get up and running with Niskala in minutes.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | For AI/ML modules |
| C++ Compiler | GCC 11+ / Clang 14+ / MSVC 2022 | For core engine |
| CMake | 3.20+ | Build system |
| Qt6 | 6.5+ | Desktop GUI (optional) |
| Docker | 20.10+ | Container deployment (optional) |

---

## Option 1: Qt6 Desktop App (Recommended)

The fastest way to get the full Niskala experience.

```bash
# Clone repository
git clone https://github.com/Allesgut7/niskala.git
cd niskala

# Build Qt6 desktop app
cd src/ui
mkdir build && cd build
cmake .. -G Ninja
ninja

# Run
./bin/niskala
```

### Qt6 Build Requirements

```bash
# Ubuntu/Debian
sudo apt install qt6-base-dev qt6-charts-dev ninja-build cmake

# macOS
brew install qt6 ninja cmake

# Windows
# Install Qt6 via Qt Online Installer
# Install Ninja: choco install ninja
```

---

## Option 2: Docker Deployment

```bash
# Clone repository
git clone https://github.com/Allesgut7/niskala.git
cd niskala

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f niskala

# Stop services
docker-compose down
```

---

## Option 3: Legacy TUI (Terminal)

For headless servers or minimal setups.

```bash
# Clone repository
git clone https://github.com/Allesgut7/niskala.git
cd niskala

# Install Python dependencies
pip install -r requirements.txt

# Build C++ terminal
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build

# Run
./build/niskala
```

---

## First Run

1. Launch Niskala
2. The terminal opens with the **Dashboard** (F1)
3. Use **F1-F7** to switch between screens
4. Type commands in the **Command Bar** (bottom)
5. Press **Ctrl+S** to save your layout

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| F1 | Dashboard |
| F2 | Chart |
| F3 | Screener |
| F4 | Portfolio |
| F5 | Market Overview |
| F6 | News |
| F7 | Settings |
| Ctrl+S | Save Layout |
| Ctrl+R | Restore Layout |
| Ctrl+Q | Quit |

---

## Command Bar

Type commands in the bottom bar:

```
DASH        → Dashboard
CHART       → Chart
SCREENER    → Screener
PORT        → Portfolio
MARKET      → Market Overview
NEWS        → News
SETTINGS    → Settings
BOOK        → Order Book
REFRESH     → Refresh Data
HELP        → Show commands
```

---

## Configuration

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
```

### Config File

Edit `config/default.json`:

```json
{
  "app": {
    "name": "Niskala",
    "version": "2.0.0"
  },
  "watchlist": ["BBCA", "BBRI", "BMRI", "TLKM", "GOTO"],
  "refresh_interval": 30,
  "theme": "dark",
  "language": "id"
}
```

---

## Troubleshooting

### Qt6 Build Issues

```bash
# Check Qt6 is installed
qmake6 --version

# If cmake can't find Qt6
export CMAKE_PREFIX_PATH=/path/to/qt6
```

### Python Module Issues

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python3 --version
```

---

## Next Steps

- Read the [README.md](README.md) for full feature list
- Check [CHANGELOG.md](CHANGELOG.md) for version history
- See [docs/API.md](docs/API.md) for REST API documentation

---

**Built for the Indonesian capital market**
