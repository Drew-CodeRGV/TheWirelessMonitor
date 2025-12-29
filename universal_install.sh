#!/bin/bash

# Universal Installation Script for The Wireless Monitor
# Works with any user, not just 'pi'

set -e

echo "🚀 Starting The Wireless Monitor installation..."

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

# Configuration - flexible paths
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/rss_aggregator"
REPO_URL="https://github.com/Drew-CodeRGV/TheWirelessMonitor.git"
SERVICE_NAME="rss-aggregator"

print_status "Installing for user: $CURRENT_USER"
print_status "Installation directory: $INSTALL_DIR"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Detected Linux system"
    if command -v apt &> /dev/null; then
        PACKAGE_MANAGER="apt"
    elif command -v yum &> /dev/null; then
        PACKAGE_MANAGER="yum"
    elif command -v pacman &> /dev/null; then
        PACKAGE_MANAGER="pacman"
    else
        print_error "Unsupported package manager"
        exit 1
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Detected macOS system"
    if command -v brew &> /dev/null; then
        PACKAGE_MANAGER="brew"
    else
        print_error "Homebrew not found. Please install Homebrew first: https://brew.sh"
        exit 1
    fi
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
case $PACKAGE_MANAGER in
    "apt")
        sudo apt update && sudo apt upgrade -y
        ;;
    "yum")
        sudo yum update -y
        ;;
    "pacman")
        sudo pacman -Syu --noconfirm
        ;;
    "brew")
        brew update
        ;;
esac

# Install system dependencies
print_status "Installing system dependencies..."
case $PACKAGE_MANAGER in
    "apt")
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
            libjpeg62-turbo-dev \
            libfreetype6-dev \
            libtiff5-dev \
            libopenjp2-7-dev \
            libwebp-dev \
            libharfbuzz-dev \
            libfribidi-dev \
            libxcb1-dev \
            zlib1g-dev \
            libffi-dev \
            libssl-dev \
            pkg-config
        ;;
    "yum")
        sudo yum install -y \
            python3 \
            python3-pip \
            git \
            curl \
            wget \
            sqlite \
            nginx \
            supervisor \
            cronie \
            gcc \
            python3-devel \
            libxml2-devel \
            libxslt-devel \
            libjpeg-devel \
            zlib-devel \
            libffi-devel \
            openssl-devel
        ;;
    "brew")
        brew install \
            python3 \
            git \
            curl \
            wget \
            sqlite \
            nginx
        ;;
esac

# Install Ollama (if not macOS or if user wants it)
if [[ "$OSTYPE" != "darwin"* ]] || [[ "$FORCE_OLLAMA" == "true" ]]; then
    print_status "Installing Ollama for AI analysis..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Start Ollama service (Linux only)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl enable ollama || true
        sudo systemctl start ollama || true
        sleep 5
    fi
    
    # Pull AI model
    print_status "Downloading AI model (this may take a while)..."
    ollama pull llama2:7b-chat || print_warning "Failed to pull AI model - you can do this later"
else
    print_warning "Skipping Ollama installation on macOS. Install manually if needed."
fi

# Create installation directory
print_status "Creating installation directory..."
mkdir -p $INSTALL_DIR

# Clone repository
print_status "Cloning repository..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd $INSTALL_DIR
    git pull origin main
else
    git clone $REPO_URL $INSTALL_DIR
    cd $INSTALL_DIR
fi

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
# Install Pillow dependencies first to avoid build issues
pip install --upgrade Pillow
pip install -r requirements.txt

# Download NLTK data
print_status "Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" || print_warning "NLTK download failed - continuing anyway"

# Create data directory
print_status "Creating data directory..."
mkdir -p $INSTALL_DIR/data
mkdir -p $INSTALL_DIR/logs

# Initialize database
print_status "Initializing database..."
python3 -c "from app.models import init_db; init_db()"

# Set up services (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Create systemd service
    print_status "Creating systemd service..."
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=RSS News Aggregator
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Configure nginx
    print_status "Configuring nginx..."
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
    }

    location /static {
        alias $INSTALL_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    # Enable nginx site
    sudo ln -sf /etc/nginx/sites-available/rss-aggregator /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl reload nginx

    # Set up cron jobs
    print_status "Setting up automated tasks..."
    (crontab -l 2>/dev/null; echo "# RSS Aggregator automated tasks") | crontab -
    (crontab -l 2>/dev/null; echo "0 */6 * * * cd $INSTALL_DIR && ./venv/bin/python scripts/daily_fetch.py >> logs/cron.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 8 * * 1 cd $INSTALL_DIR && ./venv/bin/python scripts/weekly_digest.py >> logs/cron.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 */8 * * * cd $INSTALL_DIR && ./venv/bin/python scripts/auto_update.py >> logs/update.log 2>&1") | crontab -

    # Enable and start services
    print_status "Enabling and starting services..."
    sudo systemctl daemon-reload
    sudo systemctl enable ${SERVICE_NAME}
    sudo systemctl start ${SERVICE_NAME}
    sudo systemctl enable nginx
    sudo systemctl start nginx
fi

# Create update script
print_status "Creating update script..."
tee $INSTALL_DIR/update.sh > /dev/null <<EOF
#!/bin/bash
# Update script for The Wireless Monitor

cd $INSTALL_DIR
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl restart ${SERVICE_NAME}
fi
echo "Update completed!"
EOF

chmod +x $INSTALL_DIR/update.sh

# Run initial data fetch
print_status "Running initial data fetch..."
python3 scripts/daily_fetch.py || print_warning "Initial fetch failed - you can run it later"

# Display completion message
print_success "🎉 Installation completed successfully!"
echo ""
echo "📋 System Information:"
echo "   • Installation directory: $INSTALL_DIR"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "   • Web interface: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')"
    echo "   • Service status: sudo systemctl status $SERVICE_NAME"
    echo "   • Logs: journalctl -u $SERVICE_NAME -f"
else
    echo "   • To start manually: cd $INSTALL_DIR && source venv/bin/activate && python app/main.py"
    echo "   • Web interface: http://localhost:5000"
fi
echo ""
echo "🔧 Management Commands:"
echo "   • Update system: $INSTALL_DIR/update.sh"
echo "   • Manual fetch: cd $INSTALL_DIR && ./venv/bin/python scripts/daily_fetch.py"
echo "   • View logs: tail -f $INSTALL_DIR/logs/cron.log"
echo ""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "⏰ Automated Schedule:"
    echo "   • RSS fetch: Every 6 hours"
    echo "   • Weekly digest: Monday 8:00 AM"
    echo "   • Auto-update: Every 8 hours"
    echo ""
    print_warning "The system will automatically start on boot."
fi
print_warning "Visit the web interface to add your RSS feeds!"