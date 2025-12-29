#!/bin/bash

# Fix Pillow Installation Issues on Raspberry Pi
# Run this script if you get Pillow build errors during installation

set -e

echo "🔧 Fixing Pillow installation issues..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Update package list
print_status "Updating package list..."
sudo apt update

# Install all Pillow dependencies
print_status "Installing Pillow system dependencies..."
sudo apt install -y \
    libjpeg-dev \
    libjpeg62-turbo-dev \
    libfreetype6-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    zlib1g-dev \
    pkg-config \
    build-essential \
    python3-dev

# Determine installation directory
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/rss_aggregator"

if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Installation directory not found: $INSTALL_DIR"
    print_error "Please run the main installation script first"
    exit 1
fi

cd $INSTALL_DIR

# Activate virtual environment
print_status "Activating Python virtual environment..."
source venv/bin/activate

# Upgrade pip and build tools
print_status "Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Try to install Pillow with verbose output
print_status "Installing Pillow (this may take a few minutes)..."
pip install --upgrade --force-reinstall Pillow --verbose

# Install remaining requirements
print_status "Installing remaining Python packages..."
pip install -r requirements.txt

print_success "✅ Pillow installation fixed!"
print_status "You can now continue with the main installation or restart the services."

echo ""
echo "To restart the services:"
echo "  sudo systemctl restart rss-aggregator"
echo ""
echo "To test the installation:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  python3 -c 'from PIL import Image; print(\"Pillow working!\")'"