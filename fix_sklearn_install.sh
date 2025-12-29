#!/bin/bash

# Fix scikit-learn Installation Issues on Raspberry Pi
# Run this script if you get Cython compilation errors during installation

set -e

echo "🔧 Fixing scikit-learn installation issues..."

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

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

print_status "Installing lightweight requirements without heavy scientific packages..."

# Install lightweight requirements that avoid scikit-learn compilation issues
pip install --upgrade pip setuptools wheel

# Install packages one by one with error handling
packages=(
    "Flask==2.3.3"
    "SQLAlchemy==2.0.21"
    "feedparser==6.0.10"
    "requests==2.31.0"
    "beautifulsoup4==4.12.2"
    "schedule==1.2.0"
    "python-dateutil==2.8.2"
    "Pillow"
    "nltk==3.8.1"
    "gunicorn==21.2.0"
    "PyGithub==1.59.1"
    "textblob==0.17.1"
)

for package in "${packages[@]}"; do
    print_status "Installing $package..."
    if ! pip install "$package"; then
        print_warning "Failed to install $package, continuing..."
    fi
done

# Try to install numpy and pandas (lighter versions)
print_status "Attempting to install numpy (may take time on Pi)..."
pip install "numpy>=1.19.0,<1.25.0" || print_warning "numpy installation failed - some features may be limited"

print_status "Attempting to install pandas (may take time on Pi)..."
pip install "pandas>=1.3.0,<2.1.0" || print_warning "pandas installation failed - some features may be limited"

# Skip scikit-learn entirely - the app will work without it
print_warning "Skipping scikit-learn installation to avoid compilation errors"
print_warning "The app will use simpler keyword-based analysis instead"

print_success "✅ Lightweight installation completed!"
print_status "The Wireless Monitor will work with basic text analysis instead of machine learning"

echo ""
echo "To restart the services:"
echo "  sudo systemctl restart rss-aggregator"
echo ""
echo "To test the installation:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  python3 -c 'from app.main import app; print(\"App imports successfully!\")'"