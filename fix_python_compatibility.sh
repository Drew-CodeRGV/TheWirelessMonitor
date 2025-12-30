#!/bin/bash

# Fix Python 3.13 Compatibility Issues

echo "🐍 Fixing Python 3.13 Compatibility Issues..."

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

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_status "Detected Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    print_warning "Python 3.13 detected - applying compatibility fixes..."
    
    # Create Python 3.13 compatible requirements
    cat > requirements.txt << 'EOF'
Flask==3.0.0
requests==2.31.0
feedparser==6.0.11
beautifulsoup4==4.12.2
schedule==1.2.0
EOF
    
    print_status "Updated requirements.txt for Python 3.13 compatibility"
    
elif [[ "$PYTHON_VERSION" == "3.12" ]]; then
    print_status "Python 3.12 detected - using standard requirements"
    
    cat > requirements.txt << 'EOF'
Flask==3.0.0
requests==2.31.0
feedparser==6.0.11
beautifulsoup4==4.12.2
schedule==1.2.0
EOF
    
else
    print_status "Python $PYTHON_VERSION detected - using compatible requirements"
    
    cat > requirements.txt << 'EOF'
Flask==2.3.3
requests==2.31.0
feedparser==6.0.10
beautifulsoup4==4.12.2
schedule==1.2.0
EOF
fi

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/wireless_monitor"

if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Installation directory not found: $INSTALL_DIR"
    exit 1
fi

cd "$INSTALL_DIR"

print_status "Updating Python environment..."

# Recreate virtual environment to ensure clean state
if [ -d "venv" ]; then
    print_status "Removing old virtual environment..."
    rm -rf venv
fi

print_status "Creating new virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_status "Installing compatible packages..."
pip install --upgrade pip

# Install packages one by one with error handling
packages=(
    "Flask==3.0.0"
    "requests==2.31.0" 
    "feedparser==6.0.11"
    "beautifulsoup4==4.12.2"
    "schedule==1.2.0"
)

for package in "${packages[@]}"; do
    print_status "Installing $package..."
    if pip install "$package"; then
        print_success "✓ $package installed"
    else
        print_error "✗ Failed to install $package"
        # Try without version constraint
        package_name=$(echo "$package" | cut -d'=' -f1)
        print_status "Trying $package_name without version constraint..."
        pip install "$package_name"
    fi
done

print_status "Testing imports..."
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

print_status "Testing app import..."
if PYTHONPATH="$INSTALL_DIR" python3 -c "from app.main import WirelessMonitor; print('✓ App imports successfully')"; then
    print_success "✅ All imports working!"
else
    print_error "❌ App import still failing"
    echo "Detailed error:"
    PYTHONPATH="$INSTALL_DIR" python3 -c "from app.main import WirelessMonitor"
    exit 1
fi

print_status "Restarting service..."
sudo systemctl restart wireless-monitor 2>/dev/null || true

sleep 3

if systemctl is-active --quiet wireless-monitor; then
    print_success "✅ Service restarted successfully!"
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302"; then
        print_success "✅ Web interface is working!"
        
        IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')
        echo ""
        echo "🎉 Python compatibility fixed!"
        echo "🌐 Access: http://$IP:5000"
    else
        print_warning "Service running but web interface not ready yet"
    fi
else
    print_error "Service failed to start"
    echo "Check logs: journalctl -u wireless-monitor -f"
fi

print_success "Python compatibility fix completed!"