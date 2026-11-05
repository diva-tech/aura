#!/bin/bash

# AURA v1.0 Standalone Dashboard
# Usage: ./dashboard.sh

echo "🚀 Starting AURA v1.0 Dashboard..."
echo ""

cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "🌐 Dashboard: http://localhost:8000"
echo "📊 Architecture: http://localhost:8000/#architecture"
echo "📈 Milestones: http://localhost:8000/#milestones"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 dashboard-server.py
