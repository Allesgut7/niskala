#!/bin/bash
# Niskala - Setup Script
# Version: 1.0.0

set -e

echo "============================================"
echo "  Niskala - Terminal Trading Indonesia"
echo "  Setup Script v1.0.0"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check dependencies
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}[ERROR] $1 not found. Please install it.${NC}"
        return 1
    fi
    echo -e "${GREEN}[OK] $1 found${NC}"
    return 0
}

echo "Checking system dependencies..."

# Required
MISSING=0
check_command "cmake" || MISSING=1
check_command "g++" || check_command "clang++" || MISSING=1
check_command "python3" || MISSING=1
check_command "pip3" || check_command "pip" || MISSING=1

if [ "$MISSING" -eq 1 ]; then
    echo -e "${RED}Missing dependencies. Please install them first.${NC}"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install -y cmake g++ python3 python3-pip python3-venv"
    echo "  sudo apt install -y libsqlite3-dev ninja-build"
    echo ""
    echo "macOS:"
    echo "  brew install cmake python sqlite ninja"
    exit 1
fi

# Check for Ninja (optional, faster builds)
if command -v ninja &> /dev/null; then
    GENERATOR="-G Ninja"
    echo -e "${GREEN}[OK] Ninja found - using for faster builds${NC}"
else
    GENERATOR=""
    echo -e "${YELLOW}[WARN] Ninja not found - using Make (install ninja for faster builds)${NC}"
fi

echo ""
echo "Creating directories..."
mkdir -p data/cache
mkdir -p data/local_db
mkdir -p build
mkdir -p models/finbert

echo ""
echo "Installing Python dependencies..."

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}Created Python virtual environment${NC}"
fi

# Activate venv and install
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Building C++ application..."

# Configure
cmake -B build ${GENERATOR} -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build build --config Release -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

echo ""
echo "============================================"
echo -e "${GREEN}  Setup Complete!${NC}"
echo "============================================"
echo ""
echo "Run Niskala:"
echo "  ./build/niskala"
echo ""
echo "Or with custom config:"
echo "  ./build/niskala --config config/default.json"
echo ""
echo "Keyboard shortcuts:"
echo "  F1: Dashboard  F2: Market  F3: Chart"
echo "  F4: Screener   F5: Portfolio  F6: News"
echo "  F7: Settings   q: Quit"
echo ""
