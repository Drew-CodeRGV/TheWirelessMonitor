#!/bin/bash

# Development Reset Script for The Wireless Monitor
# Quick reset for development and testing - keeps system packages

set -e

echo "🔄 Development Reset for The Wireless Monitor"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/rss_aggregator"
SERVICE_NAME="rss-aggregator"

echo ""
echo "This script will:"
echo "• Keep all system packages (Python, nginx, ollama, etc.)"
echo "• Reset the application code and configuration"
echo "• Preserve or reset database (your choice)"
echo "• Restart all services"
echo ""

if [ ! -d "$INSTALL_DIR" ]; then
    print_warning "No existing installation found. Run the main installer first."
    exit 1
fi

# Ask about database
echo "Database options:"
echo "1) Keep existing database (preserve articles and feeds)"
echo "2) Reset database (fresh start)"
echo ""
read -p "Choose option (1-2): " db_choice

# Backup database if keeping it
if [ "$db_choice" = "1" ] && [ -f "$INSTALL_DIR/data/news.db" ]; then
    print_status "Backing up database..."
    cp "$INSTALL_DIR/data/news.db" "/tmp/news_db_backup.db"
fi

print_status "Stopping services..."
sudo systemctl stop $SERVICE_NAME 2>/dev/null || true

print_status "Cleaning application files..."
cd "$INSTALL_DIR"

# Keep venv if it exists and is working
if [ -d "venv" ]; then
    print_status "Testing existing Python environment..."
    if source venv/bin/activate && python3 -c "import flask" 2>/dev/null; then
        print_status "Keeping existing Python environment"
        KEEP_VENV=true
    else
        print_status "Python environment needs refresh"
        rm -rf venv
        KEEP_VENV=false
    fi
else
    KEEP_VENV=false
fi

# Update code
print_status "Updating code from repository..."
git pull origin main || print_warning "Git pull failed, continuing..."

# Recreate venv if needed
if [ "$KEEP_VENV" = false ]; then
    print_status "Creating fresh Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install --upgrade Pillow
    
    if ! pip install -r requirements.txt; then
        print_warning "Using lightweight requirements..."
        pip install -r requirements-lite.txt
    fi
    
    python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" || true
else
    source venv/bin/activate
fi

# Handle database
mkdir -p data logs

if [ "$db_choice" = "1" ] && [ -f "/tmp/news_db_backup.db" ]; then
    print_status "Restoring database..."
    cp "/tmp/news_db_backup.db" "data/news.db"
    rm -f "/tmp/news_db_backup.db"
else
    print_status "Initializing fresh database..."
    python3 -c "from app.models import init_db; init_db()"
fi

print_status "Restarting services..."
sudo systemctl start $SERVICE_NAME
sudo systemctl reload nginx

print_status "Testing installation..."
if PYTHONPATH="$INSTALL_DIR" python3 scripts/daily_fetch.py; then
    print_success "✅ Reset completed successfully!"
else
    print_warning "Reset completed but test fetch had issues"
fi

echo ""
print_success "🎉 Development reset completed!"
echo ""
echo "📋 Status:"
echo "   • Code: Updated from repository"
echo "   • Database: $([ "$db_choice" = "1" ] && echo "Preserved" || echo "Reset")"
echo "   • Python packages: $([ "$KEEP_VENV" = true ] && echo "Preserved" || echo "Reinstalled")"
echo "   • Services: Restarted"
echo ""
echo "🌐 Web interface: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')"
echo ""
echo "Quick commands:"
echo "   • View logs: journalctl -u $SERVICE_NAME -f"
echo "   • Manual fetch: cd $INSTALL_DIR && source venv/bin/activate && PYTHONPATH=$INSTALL_DIR python3 scripts/daily_fetch.py"