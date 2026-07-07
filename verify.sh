#!/bin/bash
# Niskala - Project Verification Script
# Version: 1.0.0

echo "============================================"
echo "  Niskala - Project Verification"
echo "============================================"
echo ""

ERRORS=0

# Check directory structure
echo "Checking directory structure..."
DIRS=(
    "src/core/common"
    "src/core/market_data"
    "src/core/ai"
    "src/core/fear_greed"
    "src/core/quant"
    "src/tui/screens"
    "src/tui/widgets"
    "python/data_sources"
    "python/ai"
    "python/fear_greed"
    "python/utils"
    "config"
    "tests/unit"
    "tests/integration"
    "data/cache"
    "data/local_db"
)

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "  ❌ Missing: $dir"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -eq 0 ]; then
    echo "  ✅ All directories present"
fi

# Check critical files
echo ""
echo "Checking critical files..."
FILES=(
    "CMakeLists.txt"
    "requirements.txt"
    "setup.sh"
    "src/main.cpp"
    "src/tui/app.cpp"
    "src/tui/app.h"
    "config/default.json"
    "config/sector_mapping.json"
)

for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "  ❌ Missing: $file"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $ERRORS -eq 0 ]; then
    echo "  ✅ All critical files present"
fi

# Count files
echo ""
echo "File counts:"
echo "  C++ headers: $(find src -name "*.h" | wc -l)"
echo "  C++ sources: $(find src -name "*.cpp" | wc -l)"
echo "  Python modules: $(find python -name "*.py" | wc -l)"
echo "  Test files: $(find tests -name "*.py" | wc -l)"

# Check for TODO/stub markers
echo ""
echo "Implementation status:"
TODOS=$(grep -r "TODO" src --include="*.cpp" --include="*.h" | wc -l)
echo "  TODO markers: $TODOS"

# Check Python syntax
echo ""
echo "Checking Python syntax..."
PYTHON_ERRORS=0
for file in $(find python tests -name "*.py"); do
    python3 -m py_compile "$file" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "  ❌ Syntax error: $file"
        PYTHON_ERRORS=$((PYTHON_ERRORS + 1))
    fi
done

if [ $PYTHON_ERRORS -eq 0 ]; then
    echo "  ✅ All Python files valid"
else
    ERRORS=$((ERRORS + PYTHON_ERRORS))
fi

# Check JSON config files
echo ""
echo "Checking JSON config files..."
for file in config/*.json; do
    python3 -c "import json; json.load(open('$file'))" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "  ❌ Invalid JSON: $file"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✅ Valid: $file"
    fi
done

# Summary
echo ""
echo "============================================"
if [ $ERRORS -eq 0 ]; then
    echo "  ✅ Project verification PASSED"
    echo "============================================"
    echo ""
    echo "Ready to build. Run:"
    echo "  ./setup.sh"
    exit 0
else
    echo "  ❌ Project verification FAILED"
    echo "  Errors found: $ERRORS"
    echo "============================================"
    exit 1
fi
