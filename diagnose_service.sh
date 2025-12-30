#!/bin/bash

# Diagnostic Script for The Wireless Monitor Service Issues

echo "🔍 Diagnosing The Wireless Monitor Service..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/wireless_monitor"
SERVICE_NAME="wireless-monitor"

echo "======================================"
echo "  Service Diagnostic Report"
echo "======================================"
echo ""

# Check 1: Installation directory
print_status "Checking installation directory..."
if [ -d "$INSTALL_DIR" ]; then
    print_success "Installation directory exists: $INSTALL_DIR"
    cd "$INSTALL_DIR"
else
    print_error "Installation directory not found: $INSTALL_DIR"
    echo "Run the installer first!"
    exit 1
fi

# Check 2: Required files
print_status "Checking required files..."
if [ -f "app/main.py" ]; then
    print_success "app/main.py exists"
else
    print_error "app/main.py missing"
fi

if [ -f "requirements.txt" ]; then
    print_success "requirements.txt exists"
else
    print_error "requirements.txt missing"
fi

if [ -d "venv" ]; then
    print_success "Python virtual environment exists"
else
    print_error "Python virtual environment missing"
fi

# Check 3: Service status
print_status "Checking systemd service..."
if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME.service"; then
    print_success "Service exists in systemd"
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service is running"
    else
        print_error "Service is not running"
        echo "Service status: $(systemctl is-active $SERVICE_NAME 2>/dev/null)"
    fi
else
    print_error "Service not found in systemd"
fi

# Check 4: Port availability
print_status "Checking port 5000..."
if netstat -tlnp 2>/dev/null | grep -q ":5000 "; then
    print_success "Something is listening on port 5000"
    netstat -tlnp 2>/dev/null | grep ":5000 "
else
    print_error "Nothing listening on port 5000"
fi

# Check 5: Test Python imports
print_status "Testing Python environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    
    echo "Testing Python imports..."
    python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import flask
    print('✓ Flask imported successfully')
except ImportError as e:
    print(f'✗ Flask import failed: {e}')

try:
    import requests
    print('✓ Requests imported successfully')
except ImportError as e:
    print(f'✗ Requests import failed: {e}')

try:
    import feedparser
    print('✓ Feedparser imported successfully')
except ImportError as e:
    print(f'✗ Feedparser import failed: {e}')

try:
    from bs4 import BeautifulSoup
    print('✓ BeautifulSoup imported successfully')
except ImportError as e:
    print(f'✗ BeautifulSoup import failed: {e}')

try:
    import schedule
    print('✓ Schedule imported successfully')
except ImportError as e:
    print(f'✗ Schedule import failed: {e}')
"
else
    print_error "Virtual environment activation script not found"
fi

# Check 6: Test app import
print_status "Testing app import..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    PYTHONPATH="$INSTALL_DIR" python3 -c "
try:
    from app.main import WirelessMonitor
    print('✓ WirelessMonitor class imported successfully')
    
    # Try to create instance
    monitor = WirelessMonitor()
    print('✓ WirelessMonitor instance created successfully')
except Exception as e:
    print(f'✗ App import/creation failed: {e}')
    import traceback
    traceback.print_exc()
"
fi

# Check 7: Recent logs
print_status "Checking recent service logs..."
echo ""
echo "=== Recent Service Logs ==="
journalctl -u "$SERVICE_NAME" --no-pager -n 20 2>/dev/null || echo "No service logs available"

echo ""
echo "=== Application Logs ==="
if [ -f "logs/app.log" ]; then
    tail -20 logs/app.log
else
    echo "No application logs found"
fi

echo ""
echo "=== Error Logs ==="
if [ -f "logs/error.log" ]; then
    tail -20 logs/error.log
else
    echo "No error logs found"
fi

# Check 8: Manual start test
echo ""
print_status "Testing manual start..."
echo "Attempting to start Flask manually for 10 seconds..."

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    
    timeout 10s python3 -c "
import os
os.environ['PYTHONPATH'] = '$INSTALL_DIR'
try:
    from app.main import WirelessMonitor
    monitor = WirelessMonitor()
    print('Starting Flask manually...')
    monitor.run(host='0.0.0.0', port=5001)
except Exception as e:
    print(f'Manual start failed: {e}')
    import traceback
    traceback.print_exc()
" &
    
    MANUAL_PID=$!
    sleep 3
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 2>/dev/null | grep -q "200\|302"; then
        print_success "✅ Manual start works on port 5001!"
        echo "The app code is working. Issue is with the systemd service."
    else
        print_error "❌ Manual start failed"
        echo "There's an issue with the app code itself."
    fi
    
    kill $MANUAL_PID 2>/dev/null || true
    wait $MANUAL_PID 2>/dev/null || true
fi

echo ""
echo "======================================"
echo "  Diagnostic Summary"
echo "======================================"
echo ""
echo "Next steps based on findings:"
echo "1. If service isn't running: sudo systemctl restart wireless-monitor"
echo "2. If imports fail: cd $INSTALL_DIR && source venv/bin/activate && pip install -r requirements.txt"
echo "3. If manual start works: Check systemd service configuration"
echo "4. If manual start fails: Check Python code for errors"
echo ""
echo "Manual commands to try:"
echo "• Restart service: sudo systemctl restart wireless-monitor"
echo "• Check service status: sudo systemctl status wireless-monitor"
echo "• View live logs: journalctl -u wireless-monitor -f"
echo "• Manual start: cd $INSTALL_DIR && source venv/bin/activate && PYTHONPATH=$INSTALL_DIR python3 app/main.py"