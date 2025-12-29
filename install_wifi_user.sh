#!/bin/bash

# The Wireless Monitor Installation Script for 'wifi' user
# Specifically designed for Raspberry Pi with 'wifi' username

set -e

echo "🚀 Starting The Wireless Monitor installation for user 'wifi'..."

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

# Configuration for 'wifi' user
CURRENT_USER="wifi"
USER_HOME="/home/wifi"
INSTALL_DIR="$USER_HOME/rss_aggregator"
REPO_URL="https://github.com/Drew-CodeRGV/TheWirelessMonitor.git"
SERVICE_NAME="rss-aggregator"

# Verify we're running as the wifi user
if [ "$USER" != "wifi" ]; then
    print_error "This script should be run as the 'wifi' user"
    print_error "Current user: $USER"
    print_error "Please run: su - wifi"
    exit 1
fi

print_status "Installing for user: $CURRENT_USER"
print_status "Installation directory: $INSTALL_DIR"

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
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

# Install Ollama for AI analysis
print_status "Installing Ollama for AI analysis..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
sleep 5

# Pull a lightweight model for analysis
print_status "Downloading AI model (this may take a while)..."
ollama pull llama2:7b-chat

# Create installation directory
print_status "Creating installation directory..."
sudo mkdir -p $INSTALL_DIR
sudo chown wifi:wifi $INSTALL_DIR

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
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create data directory
print_status "Creating data directory..."
mkdir -p $INSTALL_DIR/data
mkdir -p $INSTALL_DIR/logs

# Initialize database
print_status "Initializing database..."
cd $INSTALL_DIR
python3 -c "from app.models import init_db; init_db()"

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=RSS News Aggregator
After=network.target

[Service]
Type=simple
User=wifi
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
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

# Create cron jobs for automation
print_status "Setting up automated tasks..."
(crontab -l 2>/dev/null; echo "# RSS Aggregator automated tasks") | crontab -
(crontab -l 2>/dev/null; echo "0 */6 * * * cd $INSTALL_DIR && ./venv/bin/python scripts/daily_fetch.py >> logs/cron.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 8 * * 1 cd $INSTALL_DIR && ./venv/bin/python scripts/weekly_digest.py >> logs/cron.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 */8 * * * cd $INSTALL_DIR && ./venv/bin/python scripts/auto_update.py >> logs/update.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "*/15 * * * * $INSTALL_DIR/scripts/monitor.sh >> logs/monitor.log 2>&1") | crontab -

# Create fetch script
print_status "Creating automated fetch script..."
tee $INSTALL_DIR/scripts/daily_fetch.py > /dev/null <<EOF
#!/usr/bin/env python3
"""
Daily RSS fetch and analysis script
"""
import sys
import os
sys.path.append('/home/wifi/rss_aggregator')

from app.rss_fetcher import RSSFetcher
from app.ai_analyzer import AIAnalyzer
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        logging.info("Starting daily RSS fetch...")
        
        # Fetch RSS feeds
        fetcher = RSSFetcher()
        new_articles = fetcher.fetch_all_feeds()
        
        # Analyze articles
        analyzer = AIAnalyzer()
        analyzed_count = analyzer.analyze_articles(new_articles)
        
        logging.info(f"Completed: {len(new_articles)} fetched, {analyzed_count} analyzed")
        
    except Exception as e:
        logging.error(f"Error in daily fetch: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x $INSTALL_DIR/scripts/daily_fetch.py

# Create weekly digest script
tee $INSTALL_DIR/scripts/weekly_digest.py > /dev/null <<EOF
#!/usr/bin/env python3
"""
Weekly digest generation script
"""
import sys
import os
sys.path.append('/home/wifi/rss_aggregator')

from app.ai_analyzer import AIAnalyzer
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        logging.info("Generating weekly digest...")
        
        analyzer = AIAnalyzer()
        digest = analyzer.generate_weekly_digest()
        
        logging.info("Weekly digest generated successfully")
        
    except Exception as e:
        logging.error(f"Error generating weekly digest: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x $INSTALL_DIR/scripts/weekly_digest.py

# Enable and start services
print_status "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}
sudo systemctl enable nginx
sudo systemctl start nginx

# Create update script
print_status "Creating update script..."
tee $INSTALL_DIR/update.sh > /dev/null <<EOF
#!/bin/bash
# Update script for RSS News Aggregator

cd $INSTALL_DIR
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ${SERVICE_NAME}
echo "Update completed!"
EOF

chmod +x $INSTALL_DIR/update.sh

# Final setup
print_status "Running initial data fetch..."
cd $INSTALL_DIR
source venv/bin/activate
python3 scripts/daily_fetch.py

# Display completion message
print_success "🎉 Installation completed successfully!"
echo ""
echo "📋 System Information:"
echo "   • Installation directory: $INSTALL_DIR"
echo "   • Web interface: http://$(hostname -I | awk '{print $1}')"
echo "   • Service status: sudo systemctl status $SERVICE_NAME"
echo "   • Logs: journalctl -u $SERVICE_NAME -f"
echo ""
echo "🔧 Management Commands:"
echo "   • Update system: $INSTALL_DIR/update.sh"
echo "   • Manual fetch: cd $INSTALL_DIR && ./venv/bin/python scripts/daily_fetch.py"
echo "   • View logs: tail -f $INSTALL_DIR/logs/cron.log"
echo ""
echo "⏰ Automated Schedule:"
echo "   • RSS fetch: Every 6 hours"
echo "   • Weekly digest: Monday 8:00 AM"
echo ""
print_warning "The system will automatically start on boot."
print_warning "Visit the web interface to add your RSS feeds!"

echo ""
print_success "Installation complete! Your Wireless Monitor is ready to use."