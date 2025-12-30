#!/bin/bash

# Update Service Configuration to Avoid Permission Issues

echo "⚙️ Updating service configuration..."

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/wireless_monitor"
SERVICE_NAME="wireless-monitor"

# Stop service
sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true

# Create improved service configuration
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

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service configuration updated"
echo "📋 Key changes:"
echo "   • Logs go to systemd journal (no file permission issues)"
echo "   • Added security settings"
echo "   • Explicit user and group settings"
echo ""
echo "🔧 View logs with: journalctl -u $SERVICE_NAME -f"

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl start "$SERVICE_NAME"

echo "✅ Service restarted with new configuration"