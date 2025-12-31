#!/bin/bash

# Install psutil for Raspberry Pi
echo "🔧 Installing psutil for system monitoring..."

# Try different installation methods
if command -v pip3 &> /dev/null; then
    echo "📦 Installing psutil with pip3..."
    pip3 install psutil==5.9.6
elif command -v pip &> /dev/null; then
    echo "📦 Installing psutil with pip..."
    pip install psutil==5.9.6
elif command -v apt-get &> /dev/null; then
    echo "📦 Installing psutil with apt-get..."
    sudo apt-get update
    sudo apt-get install -y python3-psutil
else
    echo "❌ No package manager found. Please install psutil manually:"
    echo "   pip3 install psutil==5.9.6"
    echo "   or"
    echo "   sudo apt-get install python3-psutil"
    exit 1
fi

echo "✅ psutil installation completed!"
echo "🔄 Please restart the wireless monitor service."