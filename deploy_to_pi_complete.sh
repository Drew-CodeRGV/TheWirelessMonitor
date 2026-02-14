#!/bin/bash

# Complete Raspberry Pi Deployment Script
# Run this script ON the Raspberry Pi after merging to main

set -e  # Exit on error

echo "=========================================="
echo "Wireless Monitor - Pi Deployment"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get current directory
PROJECT_DIR=$(pwd)
echo "Project directory: $PROJECT_DIR"
echo ""

# Step 1: Pull latest code
echo "Step 1: Pulling latest code from main..."
git checkout main
git pull origin main
echo "✅ Code updated"
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing Python dependencies..."
pip3 install --upgrade -r requirements.txt
pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client beautifulsoup4 duckduckgo-search
echo "✅ Dependencies installed"
echo ""

# Step 3: Check for credentials
echo "Step 3: Checking credentials..."
if [ ! -f "credentials.json" ]; then
    echo "⚠️  credentials.json not found!"
    echo "Please transfer it from your desktop:"
    echo "  scp credentials.json pi@$(hostname -I | awk '{print $1}'):$PROJECT_DIR/"
    read -p "Press Enter after transferring credentials.json..."
fi

if [ ! -f "token.json" ]; then
    echo "⚠️  token.json not found!"
    echo "Please transfer it from your desktop:"
    echo "  scp token.json pi@$(hostname -I | awk '{print $1}'):$PROJECT_DIR/"
    read -p "Press Enter after transferring token.json..."
fi

# Set permissions
if [ -f "credentials.json" ]; then
    chmod 600 credentials.json
    echo "✅ credentials.json permissions set"
fi

if [ -f "token.json" ]; then
    chmod 600 token.json
    echo "✅ token.json permissions set"
fi
echo ""

# Step 4: Create necessary directories
echo "Step 4: Creating directories..."
mkdir -p data logs static/generated_images
echo "✅ Directories created"
echo ""

# Step 5: Install systemd services
echo "Step 5: Installing systemd services..."

# Wireless Monitor Service
if [ -f "systemd/wireless-monitor.service" ]; then
    sudo cp systemd/wireless-monitor.service /etc/systemd/system/
    echo "✅ wireless-monitor.service installed"
else
    echo "⚠️  systemd/wireless-monitor.service not found"
fi

# Newsletter Monitor Service
if [ -f "systemd/newsletter-monitor.service" ]; then
    sudo cp systemd/newsletter-monitor.service /etc/systemd/system/
    echo "✅ newsletter-monitor.service installed"
else
    echo "⚠️  systemd/newsletter-monitor.service not found"
fi

# Reload systemd
sudo systemctl daemon-reload
echo "✅ Systemd reloaded"
echo ""

# Step 6: Enable and start services
echo "Step 6: Enabling and starting services..."

# Wireless Monitor
sudo systemctl enable wireless-monitor.service
sudo systemctl restart wireless-monitor.service
echo "✅ wireless-monitor.service started"

# Newsletter Monitor
sudo systemctl enable newsletter-monitor.service
sudo systemctl restart newsletter-monitor.service
echo "✅ newsletter-monitor.service started"
echo ""

# Step 7: Check service status
echo "Step 7: Checking service status..."
echo ""
echo "--- Wireless Monitor Service ---"
sudo systemctl status wireless-monitor.service --no-pager -l
echo ""
echo "--- Newsletter Monitor Service ---"
sudo systemctl status newsletter-monitor.service --no-pager -l
echo ""

# Step 8: Display access information
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Services Status:"
echo "  Wireless Monitor: $(systemctl is-active wireless-monitor.service)"
echo "  Newsletter Monitor: $(systemctl is-active newsletter-monitor.service)"
echo ""
echo "Access your application:"
echo "  Local: http://localhost:5000"
echo "  Network: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "View logs:"
echo "  Wireless Monitor: sudo journalctl -u wireless-monitor.service -f"
echo "  Newsletter Monitor: sudo journalctl -u newsletter-monitor.service -f"
echo "  Application: tail -f logs/app.log"
echo ""
echo "Manage services:"
echo "  Restart: sudo systemctl restart wireless-monitor.service"
echo "  Stop: sudo systemctl stop wireless-monitor.service"
echo "  Status: sudo systemctl status wireless-monitor.service"
echo ""
