#!/bin/bash

# Bootstrap Installation Script for The Wireless Monitor
# Use this script when the GitHub repository doesn't exist yet
# This script will set up the basic environment and guide you through manual setup

set -e

echo "🚀 Bootstrap Installation for The Wireless Monitor"

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

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    print_error "This script should be run as the 'pi' user"
    exit 1
fi

print_status "Starting bootstrap installation..."

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
print_status "Installing basic system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    sqlite3 \
    nginx \
    supervisor \
    cron \
    build-essential \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev

# Install Ollama
print_status "Installing Ollama for AI analysis..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
sleep 5

# Pull AI model
print_status "Downloading AI model (this may take a while)..."
ollama pull llama2:7b-chat

# Create installation directory
INSTALL_DIR="/home/pi/rss_aggregator"
print_status "Creating installation directory..."
sudo mkdir -p $INSTALL_DIR
sudo chown pi:pi $INSTALL_DIR

print_success "Bootstrap installation completed!"
echo ""
print_warning "NEXT STEPS:"
echo "1. Create your GitHub repository: https://github.com/new"
echo "   - Repository name: TheWirelessMonitor"
echo "   - Make it public"
echo ""
echo "2. Upload all project files to the repository using one of these methods:"
echo "   a) Use the GitHub web interface to upload files"
echo "   b) Use git command line to push files"
echo "   c) Use Kiro's GitHub integration (Admin → GitHub)"
echo ""
echo "3. Once the repository exists, run the full installation:"
echo "   curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/scripts/install.sh | bash"
echo ""
print_warning "The system is now prepared but needs the project files to complete installation."

# Create a reminder script
cat > $INSTALL_DIR/complete_installation.sh << 'EOF'
#!/bin/bash
echo "Completing The Wireless Monitor installation..."
echo "Checking if GitHub repository is available..."

if curl -s --head https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/scripts/install.sh | head -n 1 | grep -q "200 OK"; then
    echo "✓ Repository found! Running full installation..."
    curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/scripts/install.sh | bash
else
    echo "✗ Repository not found. Please:"
    echo "1. Create the GitHub repository"
    echo "2. Upload all project files"
    echo "3. Run this script again"
fi
EOF

chmod +x $INSTALL_DIR/complete_installation.sh

echo ""
print_success "Created completion script at: $INSTALL_DIR/complete_installation.sh"
print_status "Run this script after uploading files to GitHub to complete installation."