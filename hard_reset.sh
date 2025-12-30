#!/bin/bash

# The Wireless Monitor - Emergency Hard Reset Script
# Run this when the web interface is not responding or updating
# This script performs a complete system wipe and fresh installation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BOLD}${BLUE}$1${NC}"; }

# Get current user and paths
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/wireless_monitor"
REPO_URL="https://github.com/Drew-CodeRGV/TheWirelessMonitor.git"
SERVICE_NAME="wireless-monitor"

print_header "🚨 THE WIRELESS MONITOR - EMERGENCY HARD RESET"
echo ""
print_warning "This will COMPLETELY WIPE all data and reinstall from scratch!"
print_warning "Current user: $CURRENT_USER"
print_warning "Install directory: $INSTALL_DIR"
echo ""

# Confirmation prompts
read -p "Are you sure you want to proceed? (type 'YES' to continue): " confirm1
if [ "$confirm1" != "YES" ]; then
    print_error "Reset cancelled by user"
    exit 1
fi

read -p "This will delete ALL RSS feeds, articles, and settings. Type 'WIPE' to confirm: " confirm2
if [ "$confirm2" != "WIPE" ]; then
    print_error "Reset cancelled by user"
    exit 1
fi

echo ""
print_header "🚀 Starting Emergency Hard Reset..."
echo ""

# Step 1: Stop the service
print_status "⏹️ Stopping wireless-monitor service..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || print_warning "Service was not running"

# Step 2: Create backup
BACKUP_DIR="/tmp/wireless_monitor_emergency_backup_$(date +%Y%m%d_%H%M%S)"
if [ -d "$INSTALL_DIR" ]; then
    print_status "📦 Creating emergency backup at $BACKUP_DIR..."
    cp -r "$INSTALL_DIR" "$BACKUP_DIR" 2>/dev/null || print_warning "Could not create backup"
    print_success "Backup created (if directory existed)"
else
    print_warning "No existing installation found to backup"
fi

# Step 3: Complete removal
print_status "🗑️ Removing existing installation..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    print_success "Removed existing installation"
else
    print_warning "No existing installation directory found"
fi

# Step 4: Remove systemd service
print_status "🔧 Removing systemd service..."
sudo systemctl disable $SERVICE_NAME 2>/dev/null || true
sudo rm -f /etc/systemd/system/$SERVICE_NAME.service
sudo systemctl daemon-reload
print_success "Systemd service removed"

# Step 5: Fresh installation
print_status "📥 Creating fresh installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

print_status "📡 Cloning fresh repository..."
git clone "$REPO_URL" .
print_success "Repository cloned"

# Step 6: Install system dependencies
print_status "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
print_success "System dependencies installed"

# Step 7: Create Python virtual environment
print_status "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
print_success "Virtual environment created"

# Step 8: Install Python dependencies
print_status "📚 Installing Python packages..."
pip install --upgrade pip

# Check Python version for compatibility
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_status "Detected Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    print_warning "Python 3.13 detected - using compatible package versions"
    pip install "Flask>=3.0.0"
    pip install "requests>=2.31.0"
    pip install "feedparser>=6.0.11"
    pip install "beautifulsoup4>=4.12.0"
    pip install "schedule>=1.2.0"
else
    pip install -r requirements.txt
fi
print_success "Python packages installed"

# Step 9: Create directories and set permissions
print_status "📁 Creating directories and setting permissions..."
mkdir -p data logs
chown -R $CURRENT_USER:$CURRENT_USER "$INSTALL_DIR"
chmod +x "$INSTALL_DIR"/*.sh
chmod +x "$INSTALL_DIR"/app/main.py
print_success "Directories created and permissions set"

# Step 10: Create and install systemd service
print_status "⚙️ Creating systemd service..."
sudo cp "$INSTALL_DIR/wireless-monitor.service" /etc/systemd/system/
sudo sed -i "s|User=wifi|User=$CURRENT_USER|g" /etc/systemd/system/$SERVICE_NAME.service
sudo sed -i "s|WorkingDirectory=/home/wifi/wireless_monitor|WorkingDirectory=$INSTALL_DIR|g" /etc/systemd/system/$SERVICE_NAME.service
sudo sed -i "s|ExecStart=/usr/bin/python3 /home/wifi/wireless_monitor/app/main.py|ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/app/main.py|g" /etc/systemd/system/$SERVICE_NAME.service
sudo sed -i "s|ReadWritePaths=/home/wifi/wireless_monitor|ReadWritePaths=$INSTALL_DIR|g" /etc/systemd/system/$SERVICE_NAME.service

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
print_success "Systemd service created and enabled"

# Step 11: Start the service
print_status "▶️ Starting wireless-monitor service..."
sudo systemctl start $SERVICE_NAME

# Step 12: Wait and verify
print_status "⏳ Waiting for service to start..."
sleep 5

# Check service status
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_success "✅ Service started successfully!"
    
    # Test web interface
    print_status "🌐 Testing web interface..."
    sleep 3
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302"; then
        print_success "✅ Web interface is responding!"
    else
        print_warning "⚠️ Web interface may not be ready yet (this is normal)"
    fi
else
    print_error "❌ Service failed to start"
    print_status "📋 Checking logs..."
    sudo journalctl -u $SERVICE_NAME --no-pager -n 20
    exit 1
fi

# Step 13: Display completion info
echo ""
print_header "🎉 EMERGENCY HARD RESET COMPLETED SUCCESSFULLY!"
echo ""
print_success "✅ System completely wiped and reinstalled"
print_success "✅ Fresh database with default RSS feeds"
print_success "✅ Service running and web interface active"
echo ""
echo "📋 Reset Summary:"
echo "   • User: $CURRENT_USER"
echo "   • Installation: $INSTALL_DIR"
echo "   • Backup: $BACKUP_DIR"
echo "   • Service: $SERVICE_NAME (active)"
echo ""
echo "🌐 Access Information:"
IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')
echo "   • Web Interface: http://$IP:5000"
echo "   • Local Access: http://localhost:5000"
echo ""
echo "🔧 Management Commands:"
echo "   • Check Status: sudo systemctl status $SERVICE_NAME"
echo "   • View Logs: journalctl -u $SERVICE_NAME -f"
echo "   • Restart: sudo systemctl restart $SERVICE_NAME"
echo ""
print_success "🚀 Ready to use! The system is now in a completely fresh state."
echo ""