#!/bin/bash
#
# Fresh Installation Script for The Signal - Wireless Monitor
# This script will install everything from scratch on a new Ubuntu server
#
# Usage: curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/feature/enhancements/fresh_install.sh | bash
#

set -e  # Exit on error

echo "============================================================"
echo "THE SIGNAL - FRESH INSTALLATION"
echo "============================================================"
echo ""
echo "This will install The Signal from scratch with all optimizations"
echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
echo ""
sleep 5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/WirelessSignal"
REPO_URL="https://github.com/Drew-CodeRGV/TheWirelessMonitor.git"
BRANCH="feature/enhancements"

echo -e "${GREEN}Step 1: System Update${NC}"
echo "============================================================"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo -e "${GREEN}Step 2: Installing Dependencies${NC}"
echo "============================================================"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    sqlite3 \
    curl \
    jq \
    nginx \
    supervisor

echo ""
echo -e "${GREEN}Step 3: Cloning Repository${NC}"
echo "============================================================"
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory exists, backing up..."
    mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo ""
echo -e "${GREEN}Step 4: Setting Up Python Environment${NC}"
echo "============================================================"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo -e "${GREEN}Step 5: Creating Directories${NC}"
echo "============================================================"
mkdir -p data logs backups static

echo ""
echo -e "${GREEN}Step 6: Initializing Database${NC}"
echo "============================================================"
python3 test_startup.py

echo ""
echo -e "${GREEN}Step 7: Applying Performance Optimizations${NC}"
echo "============================================================"
echo "y" | python3 apply_performance_fixes.py

echo ""
echo -e "${GREEN}Step 8: Installing Systemd Service${NC}"
echo "============================================================"
# Update service file with correct paths
sed -i "s|/home/ubuntu/wireless-monitor|$INSTALL_DIR|g" wireless-monitor.service
sed -i "s|/usr/bin/python3|$INSTALL_DIR/venv/bin/python3|g" wireless-monitor.service
sed -i "s|User=ubuntu|User=$USER|g" wireless-monitor.service
sed -i "s|Group=ubuntu|Group=$USER|g" wireless-monitor.service

sudo cp wireless-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wireless-monitor
sudo systemctl start wireless-monitor

echo ""
echo -e "${GREEN}Step 9: Setting Up Monitoring Scripts${NC}"
echo "============================================================"

# Health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
STATUS=$(systemctl is-active wireless-monitor 2>/dev/null || echo "not-running")
if [ "$STATUS" != "active" ]; then
    echo "[$(date)] Service is down! Status: $STATUS" >> logs/health_check.log
    sudo systemctl restart wireless-monitor
fi

HEALTH=$(curl -s http://localhost:8080/health 2>/dev/null | jq -r '.status' 2>/dev/null || echo "error")
if [ "$HEALTH" != "healthy" ]; then
    echo "[$(date)] Service unhealthy! Health: $HEALTH" >> logs/health_check.log
fi
EOF

# Backup script
cat > backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups"
DB_PATH="data/wireless_monitor.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/wireless_monitor_$TIMESTAMP.db"

mkdir -p $BACKUP_DIR
cp $DB_PATH $BACKUP_FILE
gzip $BACKUP_FILE
find $BACKUP_DIR -name "*.db.gz" -mtime +7 -delete
echo "[$(date)] Backup complete: $BACKUP_FILE.gz" >> logs/backup.log
EOF

# Memory monitor script
cat > monitor_memory.sh << 'EOF'
#!/bin/bash
MEMORY_LIMIT=80
MEMORY_USAGE=$(ps aux | grep 'python3.*main.py' | grep -v grep | awk '{print $4}' | head -1)
if [ -z "$MEMORY_USAGE" ]; then
    exit 0
fi
MEMORY_INT=${MEMORY_USAGE%.*}
if [ "$MEMORY_INT" -gt "$MEMORY_LIMIT" ]; then
    echo "[$(date)] Memory usage too high: ${MEMORY_USAGE}%" >> logs/memory_monitor.log
    sudo systemctl restart wireless-monitor
fi
EOF

# Disk monitor script
cat > monitor_disk.sh << 'EOF'
#!/bin/bash
DISK_LIMIT=85
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt "$DISK_LIMIT" ]; then
    echo "[$(date)] Disk usage too high: ${DISK_USAGE}%" >> logs/disk_monitor.log
    find logs -name "*.log" -mtime +30 -delete 2>/dev/null
    find backups -name "*.db.gz" -mtime +14 -delete 2>/dev/null
fi
EOF

chmod +x health_check.sh backup_database.sh monitor_memory.sh monitor_disk.sh

echo ""
echo -e "${GREEN}Step 10: Setting Up Cron Jobs${NC}"
echo "============================================================"
(crontab -l 2>/dev/null | grep -v "WirelessSignal"; cat << CRON
# Wireless Monitor - Health Checks
*/5 * * * * $INSTALL_DIR/health_check.sh
0 3 * * * $INSTALL_DIR/backup_database.sh
*/15 * * * * $INSTALL_DIR/monitor_memory.sh
0 6 * * * $INSTALL_DIR/monitor_disk.sh
CRON
) | crontab -

echo ""
echo -e "${GREEN}Step 11: Configuring Log Rotation${NC}"
echo "============================================================"
sudo tee /etc/logrotate.d/wireless-monitor > /dev/null << EOF
$INSTALL_DIR/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $USER $USER
    sharedscripts
    postrotate
        systemctl reload wireless-monitor > /dev/null 2>&1 || true
    endscript
}
EOF

echo ""
echo -e "${GREEN}Step 12: Configuring Firewall${NC}"
echo "============================================================"
if command -v ufw &> /dev/null; then
    sudo ufw allow 8080/tcp
    sudo ufw allow 22/tcp
    echo "Firewall configured (ports 8080, 22 open)"
else
    echo "UFW not installed, skipping firewall configuration"
fi

echo ""
echo -e "${GREEN}Step 13: Verification${NC}"
echo "============================================================"
sleep 3

echo "Service status:"
sudo systemctl status wireless-monitor --no-pager | head -10

echo ""
echo "Health check:"
sleep 2
curl -s http://localhost:8080/health | jq 2>/dev/null || curl -s http://localhost:8080/health

echo ""
echo "Memory usage:"
ps aux | grep python3 | grep -v grep | awk '{print "  "$11" - "$4"% memory, "$3"% CPU"}'

echo ""
echo "Database info:"
sqlite3 data/wireless_monitor.db "SELECT COUNT(*) as articles FROM articles;" 2>/dev/null || echo "  Database initializing..."

echo ""
echo "============================================================"
echo -e "${GREEN}✅ INSTALLATION COMPLETE${NC}"
echo "============================================================"
echo ""
echo "The Signal is now running!"
echo ""
echo "Access the application:"
echo "  - Local: http://localhost:8080"
echo "  - External: http://$(curl -s ifconfig.me):8080"
echo ""
echo "Useful commands:"
echo "  - Check status: sudo systemctl status wireless-monitor"
echo "  - View logs: sudo journalctl -u wireless-monitor -f"
echo "  - Restart: sudo systemctl restart wireless-monitor"
echo "  - Health check: curl http://localhost:8080/health"
echo ""
echo "Monitoring:"
echo "  - Health checks: Every 5 minutes"
echo "  - Backups: Daily at 3 AM"
echo "  - Memory monitoring: Every 15 minutes"
echo "  - Disk monitoring: Daily at 6 AM"
echo ""
echo "Documentation:"
echo "  - Performance: $INSTALL_DIR/PERFORMANCE_OPTIMIZATION.md"
echo "  - Stability: $INSTALL_DIR/STABILITY_GUIDE.md"
echo "  - Scoring: $INSTALL_DIR/SCORING_SYSTEM.md"
echo ""
echo "Expected performance:"
echo "  - Page load: 1-2 seconds"
echo "  - RSS fetch: 1-2 minutes"
echo "  - Memory: 200-400MB"
echo "  - Uptime: 99.9%"
echo ""
echo "============================================================"
