#!/bin/bash

# Manual Test Script - Run Flask App Directly

echo "🧪 Testing Flask App Manually"

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/wireless_monitor"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Installation directory not found: $INSTALL_DIR"
    echo "Run the installer first!"
    exit 1
fi

cd "$INSTALL_DIR"

if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found"
    exit 1
fi

echo "📁 Working directory: $(pwd)"
echo "🐍 Activating Python environment..."
source venv/bin/activate

echo "📦 Checking Python packages..."
pip list | grep -E "(Flask|requests|feedparser|beautifulsoup4|schedule)"

echo ""
echo "🚀 Starting Flask app manually..."
echo "This will run on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Set environment and run
export PYTHONPATH="$INSTALL_DIR"
python3 app/main.py