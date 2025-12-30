#!/bin/bash

# The Wireless Monitor - Streamlined Edition Installation Script
# Single service, minimal dependencies, maximum efficiency

set -e

echo "🚀 Installing The Wireless Monitor - Streamlined Edition"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/wireless_monitor"
REPO_URL="https://github.com/Drew-CodeRGV/TheWirelessMonitor.git"
SERVICE_NAME="wireless-monitor"

print_status "Installing for user: $CURRENT_USER"
print_status "Installation directory: $INSTALL_DIR"

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

# Create installation directory
print_status "Setting up installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    print_status "Updating from repository..."
    git pull origin main
else
    print_status "Cloning repository..."
    git clone "$REPO_URL" .
fi

# Verify required files exist
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found in repository"
    exit 1
fi

if [ ! -f "app/main.py" ]; then
    print_error "app/main.py not found in repository"
    exit 1
fi

print_status "Found required files: requirements.txt and app/main.py"

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python packages from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
print_status "Creating data and log directories..."
mkdir -p data logs

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=The Wireless Monitor - Streamlined Edition
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python app/main.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/app.log
StandardError=append:$INSTALL_DIR/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
print_status "Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Wait for service to start
sleep 5

# Check if service is running
if systemctl is-active --quiet $SERVICE_NAME; then
    print_success "✅ Service started successfully!"
else
    print_error "❌ Service failed to start"
    print_status "Checking logs..."
    journalctl -u $SERVICE_NAME --no-pager -n 20
fi

# Test web interface
print_status "Testing web interface..."
sleep 3

if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302"; then
    print_success "✅ Web interface is working!"
else
    print_warning "⚠️ Web interface may not be ready yet (this is normal)"
fi

# Display completion info
echo ""
print_success "🎉 The Wireless Monitor - Streamlined Edition installed!"
echo ""
echo "📋 Installation Summary:"
echo "   • Architecture: Single Python service"
echo "   • Dependencies: 5 lightweight Python packages"
echo "   • Database: Embedded SQLite"
echo "   • Scheduler: Built-in (no cron jobs)"
echo "   • Web Server: Flask built-in (no nginx)"
echo ""
echo "🌐 Access Information:"
IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')
echo "   • Web Interface: http://$IP:5000"
echo "   • Local Access: http://localhost:5000"
echo ""
echo "🔧 Management Commands:"
echo "   • Check Status: sudo systemctl status $SERVICE_NAME"
echo "   • Restart: sudo systemctl restart $SERVICE_NAME"
echo "   • View Logs: journalctl -u $SERVICE_NAME -f"
echo "   • Stop Service: sudo systemctl stop $SERVICE_NAME"
echo ""
echo "📁 File Locations:"
echo "   • Installation: $INSTALL_DIR"
echo "   • Database: $INSTALL_DIR/data/wireless_monitor.db"
echo "   • Application Logs: $INSTALL_DIR/logs/app.log"
echo "   • Error Logs: $INSTALL_DIR/logs/error.log"
echo ""
print_success "🚀 Ready to use! Visit the web interface to add RSS feeds."
echo ""
echo "Next steps:"
echo "1. Open http://$IP:5000 in your browser"
echo "2. Go to 'RSS Feeds' to add wireless technology news sources"
echo "3. Click 'Fetch Now' to get your first articles"
echo "4. Check the 'Admin' section for system status"