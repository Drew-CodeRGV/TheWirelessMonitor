#!/bin/bash

# Fix 502 Bad Gateway Error for The Wireless Monitor
# Diagnoses and fixes common causes of nginx 502 errors

echo "🔧 Diagnosing 502 Bad Gateway Error..."

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

echo ""
echo "=== 502 Bad Gateway Diagnostic ==="
echo ""

# Check 1: Installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Installation directory not found: $INSTALL_DIR"
    echo "Run the installer first!"
    exit 1
fi

cd "$INSTALL_DIR"

# Check 2: Service status
print_status "Checking service status..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_success "Service $SERVICE_NAME is running"
else
    print_error "Service $SERVICE_NAME is not running"
    print_status "Service status: $(systemctl is-active $SERVICE_NAME 2>/dev/null)"
    
    print_status "Attempting to start service..."
    sudo systemctl start "$SERVICE_NAME"
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service started successfully"
    else
        print_error "Failed to start service"
        print_status "Checking service logs..."
        journalctl -u "$SERVICE_NAME" --no-pager -n 20
        echo ""
    fi
fi

# Check 3: Port 5000 accessibility
print_status "Checking if Flask app is responding on port 5000..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302\|404"; then
    print_success "Flask app is responding on port 5000"
else
    print_error "Flask app is not responding on port 5000"
    
    # Check if something else is using port 5000
    PORT_USER=$(lsof -ti:5000 2>/dev/null)
    if [ -n "$PORT_USER" ]; then
        print_warning "Port 5000 is in use by process: $PORT_USER"
        ps -p "$PORT_USER" -o pid,ppid,cmd --no-headers 2>/dev/null || true
    else
        print_warning "Nothing is listening on port 5000"
    fi
    
    # Try to start Flask manually
    print_status "Attempting to start Flask manually..."
    source venv/bin/activate
    
    # Check if we can import the app
    if PYTHONPATH="$INSTALL_DIR" python3 -c "from app.main import app; print('App imports successfully')" 2>/dev/null; then
        print_success "App imports successfully"
        
        # Try to run it
        print_status "Starting Flask in background for testing..."
        PYTHONPATH="$INSTALL_DIR" python3 -c "
from app.main import app
import sys
try:
    print('Starting Flask app...')
    app.run(host='0.0.0.0', port=5000, debug=False)
except Exception as e:
    print(f'Error starting Flask: {e}')
    sys.exit(1)
" &
        
        FLASK_PID=$!
        sleep 5
        
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302\|404"; then
            print_success "Flask started manually and is responding"
            kill $FLASK_PID 2>/dev/null || true
        else
            print_error "Flask failed to start manually"
            kill $FLASK_PID 2>/dev/null || true
        fi
    else
        print_error "App import failed - checking Python path issues..."
        PYTHONPATH="$INSTALL_DIR" python3 -c "from app.main import app" 2>&1 | head -10
    fi
fi

# Check 4: Nginx configuration
print_status "Checking nginx configuration..."
if [ -f "/etc/nginx/sites-available/rss-aggregator" ]; then
    print_success "Nginx config file exists"
    
    if [ -L "/etc/nginx/sites-enabled/rss-aggregator" ]; then
        print_success "Nginx config is enabled"
    else
        print_warning "Nginx config exists but not enabled"
        print_status "Enabling nginx config..."
        sudo ln -sf /etc/nginx/sites-available/rss-aggregator /etc/nginx/sites-enabled/
    fi
    
    # Test nginx config
    if sudo nginx -t 2>/dev/null; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration has errors:"
        sudo nginx -t
    fi
else
    print_error "Nginx config file missing"
    print_status "Creating nginx configuration..."
    
    sudo tee /etc/nginx/sites-available/rss-aggregator > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias $INSTALL_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/rss-aggregator /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    print_success "Nginx configuration created"
fi

# Check 5: Nginx service
print_status "Checking nginx service..."
if systemctl is-active --quiet nginx; then
    print_success "Nginx is running"
else
    print_error "Nginx is not running"
    print_status "Starting nginx..."
    sudo systemctl start nginx
fi

# Reload nginx to pick up config changes
print_status "Reloading nginx configuration..."
sudo systemctl reload nginx

# Check 6: Firewall/iptables
print_status "Checking if port 80 is accessible..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null | grep -q "502"; then
    print_warning "Getting 502 error - this confirms nginx is working but can't reach Flask"
elif curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null | grep -q "200\|302\|404"; then
    print_success "Port 80 is accessible and working!"
else
    print_warning "Port 80 may be blocked or nginx not responding"
fi

# Check 7: System resources
print_status "Checking system resources..."
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
print_status "Memory usage: ${MEMORY_USAGE}%"

if [ -f "/proc/loadavg" ]; then
    LOAD_AVG=$(cat /proc/loadavg | cut -d' ' -f1)
    print_status "Load average: $LOAD_AVG"
fi

# Check 8: Recent logs
print_status "Checking recent error logs..."
echo ""
echo "=== Recent Service Logs ==="
journalctl -u "$SERVICE_NAME" --no-pager -n 10 --since "5 minutes ago" 2>/dev/null || echo "No recent service logs"

echo ""
echo "=== Recent Nginx Error Logs ==="
sudo tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error logs found"

# Attempt automatic fix
echo ""
print_status "Attempting automatic fix..."

# Stop and restart services in correct order
print_status "Restarting services..."
sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
sleep 2
sudo systemctl start "$SERVICE_NAME"
sleep 3
sudo systemctl reload nginx

# Final test
print_status "Testing final result..."
sleep 2

if curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null | grep -q "200\|302\|404"; then
    print_success "✅ 502 error fixed! Website should be working now."
    IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')
    echo ""
    echo "🌐 Try accessing: http://$IP"
elif curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null | grep -q "502"; then
    print_error "❌ Still getting 502 error"
    echo ""
    echo "Manual troubleshooting steps:"
    echo "1. Check service logs: journalctl -u $SERVICE_NAME -f"
    echo "2. Try manual start: cd $INSTALL_DIR && source venv/bin/activate && PYTHONPATH=$INSTALL_DIR python3 app/main.py"
    echo "3. Check Python dependencies: cd $INSTALL_DIR && source venv/bin/activate && pip list"
else
    print_warning "❓ Unexpected response - check manually"
fi

echo ""
echo "=== Diagnostic Complete ==="