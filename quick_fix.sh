#!/bin/bash

# Quick Fix Script for The Wireless Monitor

echo "🔧 Quick Fix for The Wireless Monitor"

# Colors
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
SERVICE_NAME="wireless-monitor"

if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Installation directory not found: $INSTALL_DIR"
    echo "Please run the installer first!"
    exit 1
fi

cd "$INSTALL_DIR"

print_status "Step 1: Stopping existing service..."
sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true

print_status "Step 2: Checking Python environment..."
if [ ! -d "venv" ]; then
    print_warning "Virtual environment missing, creating..."
    python3 -m venv venv
fi

source venv/bin/activate

print_status "Step 3: Installing/updating Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

print_status "Step 4: Creating directories..."
mkdir -p data logs

print_status "Step 5: Testing app import..."
if PYTHONPATH="$INSTALL_DIR" python3 -c "from app.main import WirelessMonitor; print('✓ Import successful')"; then
    print_success "App imports correctly"
else
    print_error "App import failed"
    echo "Checking for specific errors..."
    PYTHONPATH="$INSTALL_DIR" python3 -c "from app.main import WirelessMonitor"
    exit 1
fi

print_status "Step 6: Recreating systemd service..."
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

print_status "Step 7: Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

print_status "Step 8: Waiting for service to start..."
sleep 5

if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_success "✅ Service is running!"
else
    print_error "❌ Service failed to start"
    echo ""
    echo "Service logs:"
    journalctl -u "$SERVICE_NAME" --no-pager -n 10
    echo ""
    echo "Trying manual start to debug..."
    
    print_status "Manual test (will run for 10 seconds)..."
    timeout 10s python3 app/main.py &
    MANUAL_PID=$!
    sleep 3
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302"; then
        print_success "✅ Manual start works - service configuration issue"
    else
        print_error "❌ Manual start also fails - app code issue"
    fi
    
    kill $MANUAL_PID 2>/dev/null || true
    wait $MANUAL_PID 2>/dev/null || true
    exit 1
fi

print_status "Step 9: Testing web interface..."
sleep 3

if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302"; then
    print_success "✅ Web interface is working!"
    
    IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')
    echo ""
    echo "🎉 The Wireless Monitor is now running!"
    echo ""
    echo "🌐 Access URLs:"
    echo "   • Local: http://localhost:5000"
    echo "   • Network: http://$IP:5000"
    echo ""
    echo "🔧 Management:"
    echo "   • Status: sudo systemctl status $SERVICE_NAME"
    echo "   • Logs: journalctl -u $SERVICE_NAME -f"
    echo "   • Restart: sudo systemctl restart $SERVICE_NAME"
    
else
    print_warning "⚠️ Service is running but web interface not responding"
    echo "Check logs: journalctl -u $SERVICE_NAME -f"
fi