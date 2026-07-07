#!/bin/bash
# Quick syntax check without full build

echo "=== Checking C++ syntax with g++ ==="
find src -name "*.cpp" | while read f; do
    echo "Checking $f..."
    g++ -std=c++20 -Isrc -fsyntax-only -c "$f" 2>&1 | head -20
done

echo ""
echo "=== File count summary ==="
echo "Headers: $(find src -name "*.h" | wc -l)"
echo "Sources: $(find src -name "*.cpp" | wc -l)"
echo "Total: $(find src -name "*.h" -o -name "*.cpp" | wc -l)"
