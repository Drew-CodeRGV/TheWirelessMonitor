#!/bin/bash

# Debug Service Issues - Test different ways to run the Flask app

echo "🔍 Debugging Service Issues"

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
INSTALL_DIR="$USER_HOME/rss_aggregator"
SERVICE_NAME="rss-aggregator"

if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Installation directory not found: $INSTALL_DIR"
    exit 1
fi

cd "$INSTALL_DIR"
source venv/bin/activate

echo ""
echo "=== Service Debug Information ==="
echo ""

# Check systemd service file
print_status "Checking systemd service configuration..."
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    print_success "Service file exists"
    echo ""
    echo "Current service configuration:"
    cat "/etc/systemd/system/$SERVICE_NAME.service"
    echo ""
else
    print_error "Service file missing"
    print_status "Creating service file..."
    
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=The Wireless Monitor RSS Aggregator
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 --log-level info app.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    print_success "Service file created"
fi

# Test gunicorn directly
print_status "Testing gunicorn directly..."
echo "Running: gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 30 app.main:app"
echo "This will run for 10 seconds then stop..."

timeout 10s gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 30 --log-level debug app.main:app &
GUNICORN_PID=$!

sleep 3

if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302\|404"; then
    print_success "✅ Gunicorn works directly"
    GUNICORN_WORKS=true
else
    print_error "❌ Gunicorn failed directly"
    GUNICORN_WORKS=false
fi

# Stop the test gunicorn
kill $GUNICORN_PID 2>/dev/null || true
wait $GUNICORN_PID 2>/dev/null || true

# Test Flask development server
print_status "Testing Flask development server..."
echo "Running Flask dev server for 10 seconds..."

timeout 10s python3 -c "
import os
os.environ['PYTHONPATH'] = '$INSTALL_DIR'
from app.main import app
app.run(host='0.0.0.0', port=5000, debug=False)
" &
FLASK_PID=$!

sleep 3

if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302\|404"; then
    print_success "✅ Flask dev server works"
    FLASK_WORKS=true
else
    print_error "❌ Flask dev server failed"
    FLASK_WORKS=false
fi

# Stop the test flask
kill $FLASK_PID 2>/dev/null || true
wait $FLASK_PID 2>/dev/null || true

# Check service logs
print_status "Checking service logs..."
echo ""
echo "=== Recent Service Logs ==="
journalctl -u "$SERVICE_NAME" --no-pager -n 20 2>/dev/null || echo "No service logs available"

# Check if gunicorn is installed properly
print_status "Checking gunicorn installation..."
if command -v gunicorn >/dev/null; then
    print_success "Gunicorn is available in PATH"
    gunicorn --version
else
    print_warning "Gunicorn not in PATH, checking venv..."
    if [ -f "venv/bin/gunicorn" ]; then
        print_success "Gunicorn found in venv"
        ./venv/bin/gunicorn --version
    else
        print_error "Gunicorn not found"
        print_status "Installing gunicorn..."
        pip install gunicorn
    fi
fi

# Recommendations
echo ""
echo "=== Diagnosis Results ==="
if [ "$GUNICORN_WORKS" = true ] && [ "$FLASK_WORKS" = true ]; then
    print_success "Both Flask and Gunicorn work - issue is likely with systemd service"
    echo ""
    echo "Try these steps:"
    echo "1. sudo systemctl stop $SERVICE_NAME"
    echo "2. sudo systemctl daemon-reload"
    echo "3. sudo systemctl start $SERVICE_NAME"
    echo "4. sudo systemctl status $SERVICE_NAME"
    
elif [ "$FLASK_WORKS" = true ] && [ "$GUNICORN_WORKS" = false ]; then
    print_warning "Flask works but Gunicorn doesn't - Gunicorn configuration issue"
    echo ""
    echo "Try running manually:"
    echo "cd $INSTALL_DIR"
    echo "source venv/bin/activate"
    echo "PYTHONPATH=$INSTALL_DIR gunicorn --bind 0.0.0.0:5000 --workers 1 --log-level debug app.main:app"
    
elif [ "$FLASK_WORKS" = false ]; then
    print_error "Flask app has issues - check Python dependencies and imports"
    echo ""
    echo "Try:"
    echo "cd $INSTALL_DIR"
    echo "source venv/bin/activate"
    echo "PYTHONPATH=$INSTALL_DIR python3 -c 'from app.main import app; print(\"Import successful\")'"
    
else
    print_success "Everything seems to work - check service configuration"
fi

echo ""
echo "Manual service restart:"
echo "sudo systemctl restart $SERVICE_NAME && sudo systemctl status $SERVICE_NAME"