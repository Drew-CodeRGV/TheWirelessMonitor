#!/bin/bash

# Fix All Permission Issues for The Wireless Monitor

echo "🔐 Fixing Permission Issues..."

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
    exit 1
fi

print_status "Current user: $CURRENT_USER"
print_status "Installation directory: $INSTALL_DIR"

# Stop service first
print_status "Stopping service..."
sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true

cd "$INSTALL_DIR"

# Fix ownership of entire directory
print_status "Fixing directory ownership..."
sudo chown -R "$CURRENT_USER:$CURRENT_USER" "$INSTALL_DIR"

# Create directories with proper permissions
print_status "Creating directories with proper permissions..."
mkdir -p data logs
chmod 755 data logs

# Create log files with proper permissions
print_status "Creating log files..."
touch logs/app.log logs/error.log
chmod 644 logs/app.log logs/error.log

# Fix Python virtual environment permissions
if [ -d "venv" ]; then
    print_status "Fixing virtual environment permissions..."
    chmod -R 755 venv
fi

# Make main.py executable
print_status "Making main.py executable..."
chmod +x app/main.py

# Update systemd service to handle permissions better
print_status "Updating systemd service configuration..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=The Wireless Monitor - Streamlined Edition
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python app/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=wireless-monitor

[Install]
WantedBy=multi-user.target
EOF

print_status "Reloading systemd configuration..."
sudo systemctl daemon-reload

# Test permissions before starting service
print_status "Testing file permissions..."
if [ -w "logs/app.log" ]; then
    print_success "✓ app.log is writable"
else
    print_error "✗ app.log is not writable"
    chmod 644 logs/app.log
fi

if [ -w "data" ]; then
    print_success "✓ data directory is writable"
else
    print_error "✗ data directory is not writable"
    chmod 755 data
fi

# Update main.py to handle logging better
print_status "Updating logging configuration in main.py..."
python3 << 'EOF'
import os
import sys

# Read the current main.py
with open('app/main.py', 'r') as f:
    content = f.read()

# Replace the logging configuration to be more robust
old_logging = '''# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)'''

new_logging = '''# Configure logging with better error handling
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Create handlers with error handling
handlers = [logging.StreamHandler()]
try:
    log_file = os.path.join(log_dir, 'app.log')
    # Ensure log file exists and is writable
    if not os.path.exists(log_file):
        open(log_file, 'a').close()
    handlers.append(logging.FileHandler(log_file))
except (PermissionError, OSError) as e:
    print(f"Warning: Could not create log file: {e}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)'''

if old_logging in content:
    content = content.replace(old_logging, new_logging)
    with open('app/main.py', 'w') as f:
        f.write(content)
    print("✓ Updated logging configuration")
else:
    print("✓ Logging configuration already updated or different")
EOF

# Start service
print_status "Starting service..."
sudo systemctl start "$SERVICE_NAME"

# Wait and check
sleep 5

if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_success "✅ Service started successfully!"
    
    # Test web interface
    sleep 3
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302"; then
        print_success "✅ Web interface is working!"
        
        IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')
        echo ""
        echo "🎉 Permission issues fixed!"
        echo "🌐 Access: http://$IP:5000"
        echo ""
        echo "📁 File permissions:"
        ls -la logs/
        echo ""
        echo "🔧 Service status:"
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
    else
        print_warning "Service running but web interface not responding"
    fi
else
    print_error "❌ Service failed to start"
    echo ""
    echo "Service logs:"
    journalctl -u "$SERVICE_NAME" --no-pager -n 20
    echo ""
    echo "File permissions:"
    ls -la logs/ data/
fi

print_status "Permission fix completed!"
echo ""
echo "🔧 Useful commands:"
echo "• Check service: sudo systemctl status $SERVICE_NAME"
echo "• View logs: journalctl -u $SERVICE_NAME -f"
echo "• Check permissions: ls -la $INSTALL_DIR/logs/"
echo "• Manual test: cd $INSTALL_DIR && source venv/bin/activate && python3 app/main.py"