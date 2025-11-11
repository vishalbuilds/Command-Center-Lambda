#!/bin/sh
set -e

echo "🟢 Running tests during Docker build..."
echo ""

# Run pytest tests
echo "=========================================="
echo "  Running pytest unit tests..."
echo "=========================================="

cd /var/task

if python -m pytest test_unit/ -v --tb=short; then
    echo ""
    echo "=========================================="
    echo "✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅"
    echo "          🎉 TESTS PASSED 🎉"
    echo "✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅"
    echo "=========================================="
    echo ""
    echo "✅ Build can continue..."
else
    echo ""
    echo "=========================================="
    echo "❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌"
    echo "          💥 TESTS FAILED 💥"
    echo "❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌"
    echo "=========================================="
    echo ""
    echo "🛑 Build failed - Fix tests first!"
    exit 1
fi
