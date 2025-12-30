#!/bin/bash

# The Wireless Monitor - System Reset Script
# This script wipes all data and reinstalls the system from scratch

set -e

echo "🚨 Starting system reset..."

# Get current user and paths
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/wireless_monitor"

# Stop the service
echo "⏹️ Stopping wireless-monitor service..."
sudo systemctl stop wireless-monitor || true

# Backup current directory
BACKUP_DIR="/tmp/wireless_monitor_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup at $BACKUP_DIR..."
cp -r "$INSTALL_DIR" "$BACKUP_DIR" || true

# Change to project directory
cd "$INSTALL_DIR"

# Pull latest changes from GitHub
echo "📥 Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main
git clean -fd

# Remove all data and logs
echo "🗑️ Removing all data and logs..."
rm -rf data/
rm -rf logs/
rm -f *.log

# Recreate directories
echo "📁 Creating fresh directories..."
mkdir -p data
mkdir -p logs

# Activate virtual environment and update dependencies
echo "🐍 Updating Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Fix permissions
echo "🔐 Setting correct permissions..."
chown -R $CURRENT_USER:$CURRENT_USER "$INSTALL_DIR"
chmod +x "$INSTALL_DIR"/*.sh
chmod +x "$INSTALL_DIR"/app/main.py

# Update systemd service
echo "⚙️ Updating systemd service..."
sudo cp "$INSTALL_DIR/wireless-monitor.service" /etc/systemd/system/
sudo sed -i "s|User=wifi|User=$CURRENT_USER|g" /etc/systemd/system/wireless-monitor.service
sudo sed -i "s|WorkingDirectory=/home/wifi/wireless_monitor|WorkingDirectory=$INSTALL_DIR|g" /etc/systemd/system/wireless-monitor.service
sudo sed -i "s|ExecStart=/usr/bin/python3 /home/wifi/wireless_monitor/app/main.py|ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/app/main.py|g" /etc/systemd/system/wireless-monitor.service
sudo sed -i "s|ReadWritePaths=/home/wifi/wireless_monitor|ReadWritePaths=$INSTALL_DIR|g" /etc/systemd/system/wireless-monitor.service

sudo systemctl daemon-reload
sudo systemctl enable wireless-monitor

# Start the service
echo "▶️ Starting wireless-monitor service..."
sudo systemctl start wireless-monitor

# Wait a moment for service to start
sleep 3

# Check service status
if sudo systemctl is-active --quiet wireless-monitor; then
    echo "✅ System reset completed successfully!"
    echo "📊 Service is running"
    echo "🔗 Access the web interface at http://localhost:5000"
    echo "📦 Backup saved at: $BACKUP_DIR"
else
    echo "❌ Service failed to start after reset"
    echo "📋 Check logs: sudo journalctl -u wireless-monitor -f"
    exit 1
fi

echo "🎉 Reset complete! The system is now in a fresh state with default settings."