#!/bin/bash

# Status Checker for The Wireless Monitor
# Shows what's installed and working

echo "🔍 The Wireless Monitor - System Status Check"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_check() {
    if [ "$2" = "true" ]; then
        echo -e "   ${GREEN}✓${NC} $1"
    else
        echo -e "   ${RED}✗${NC} $1"
    fi
}

print_info() {
    echo -e "   ${BLUE}ℹ${NC} $1"
}

print_section() {
    echo -e "\n${CYAN}$1${NC}"
    echo "----------------------------------------"
}

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/rss_aggregator"
SERVICE_NAME="rss-aggregator"

print_section "System Information"
print_info "User: $CURRENT_USER"
print_info "Home: $USER_HOME"
print_info "Install Directory: $INSTALL_DIR"
if [ -f /proc/device-tree/model ]; then
    MODEL=$(cat /proc/device-tree/model 2>/dev/null | tr -d '\0')
    print_info "Device: $MODEL"
fi

print_section "System Packages"
print_check "Python 3" "$(command -v python3 >/dev/null && echo true || echo false)"
print_check "Git" "$(command -v git >/dev/null && echo true || echo false)"
print_check "Nginx" "$(command -v nginx >/dev/null && echo true || echo false)"
print_check "SQLite" "$(command -v sqlite3 >/dev/null && echo true || echo false)"
print_check "Ollama" "$(command -v ollama >/dev/null && echo true || echo false)"

if command -v ollama >/dev/null; then
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_check "Ollama Service" "true"
        MODELS=$(ollama list 2>/dev/null | grep -v "NAME" | wc -l)
        print_info "AI Models installed: $MODELS"
    else
        print_check "Ollama Service" "false"
    fi
fi

print_section "Application Installation"
print_check "Install Directory" "$([ -d "$INSTALL_DIR" ] && echo true || echo false)"
print_check "Git Repository" "$([ -d "$INSTALL_DIR/.git" ] && echo true || echo false)"
print_check "Python Virtual Env" "$([ -d "$INSTALL_DIR/venv" ] && echo true || echo false)"
print_check "Database File" "$([ -f "$INSTALL_DIR/data/news.db" ] && echo true || echo false)"
print_check "Application Code" "$([ -f "$INSTALL_DIR/app/main.py" ] && echo true || echo false)"

if [ -f "$INSTALL_DIR/version.json" ]; then
    VERSION=$(cat "$INSTALL_DIR/version.json" 2>/dev/null | grep -o '"version":"[^"]*' | cut -d'"' -f4)
    print_info "Version: $VERSION"
fi

print_section "System Services"
if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME.service"; then
    print_check "Systemd Service Exists" "true"
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_check "Service Running" "true"
    else
        print_check "Service Running" "false"
        print_info "Status: $(systemctl is-active $SERVICE_NAME 2>/dev/null || echo 'unknown')"
    fi
else
    print_check "Systemd Service Exists" "false"
fi

if systemctl is-active --quiet nginx; then
    print_check "Nginx Running" "true"
else
    print_check "Nginx Running" "false"
fi

print_check "Nginx Config" "$([ -f "/etc/nginx/sites-available/rss-aggregator" ] && echo true || echo false)"

print_section "Web Interface"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null | grep -q "200\|302"; then
    print_check "App Server (Port 5000)" "true"
else
    print_check "App Server (Port 5000)" "false"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null | grep -q "200\|302"; then
    print_check "Web Interface (Port 80)" "true"
    IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')
    print_info "Access at: http://$IP"
else
    print_check "Web Interface (Port 80)" "false"
fi

print_section "Database Status"
if [ -f "$INSTALL_DIR/data/news.db" ]; then
    FEEDS=$(sqlite3 "$INSTALL_DIR/data/news.db" "SELECT COUNT(*) FROM rss_feeds;" 2>/dev/null || echo "0")
    ARTICLES=$(sqlite3 "$INSTALL_DIR/data/news.db" "SELECT COUNT(*) FROM articles;" 2>/dev/null || echo "0")
    ACTIVE_FEEDS=$(sqlite3 "$INSTALL_DIR/data/news.db" "SELECT COUNT(*) FROM rss_feeds WHERE active=1;" 2>/dev/null || echo "0")
    
    print_info "Total RSS Feeds: $FEEDS"
    print_info "Active RSS Feeds: $ACTIVE_FEEDS"
    print_info "Total Articles: $ARTICLES"
    
    if [ "$ARTICLES" -gt 0 ]; then
        RECENT=$(sqlite3 "$INSTALL_DIR/data/news.db" "SELECT COUNT(*) FROM articles WHERE DATE(published_date) >= DATE('now', '-1 day');" 2>/dev/null || echo "0")
        print_info "Articles (last 24h): $RECENT"
    fi
fi

print_section "Automation Status"
CRON_JOBS=$(crontab -l 2>/dev/null | grep -c "rss_aggregator\|RSS Aggregator" || echo "0")
print_info "Cron Jobs: $CRON_JOBS"

if [ "$CRON_JOBS" -gt 0 ]; then
    print_info "Scheduled tasks:"
    crontab -l 2>/dev/null | grep "rss_aggregator\|RSS Aggregator" | while read line; do
        if [[ $line == *"daily_fetch"* ]]; then
            print_info "  • RSS Fetch: Every 6 hours"
        elif [[ $line == *"weekly_digest"* ]]; then
            print_info "  • Weekly Digest: Monday 8 AM"
        elif [[ $line == *"auto_update"* ]]; then
            print_info "  • Auto Update: Every 8 hours"
        elif [[ $line == *"monitor"* ]]; then
            print_info "  • Health Monitor: Every 15 minutes"
        fi
    done
fi

print_section "Recent Logs"
if [ -f "$INSTALL_DIR/logs/cron.log" ]; then
    LAST_FETCH=$(tail -n 20 "$INSTALL_DIR/logs/cron.log" 2>/dev/null | grep "Starting daily RSS fetch" | tail -1 | cut -d' ' -f1-2)
    if [ -n "$LAST_FETCH" ]; then
        print_info "Last RSS fetch: $LAST_FETCH"
    fi
fi

if systemctl is-active --quiet "$SERVICE_NAME"; then
    MEMORY=$(systemctl show "$SERVICE_NAME" --property=MemoryCurrent --value 2>/dev/null)
    if [ -n "$MEMORY" ] && [ "$MEMORY" != "0" ]; then
        MEMORY_MB=$((MEMORY / 1024 / 1024))
        print_info "Memory usage: ${MEMORY_MB}MB"
    fi
fi

print_section "Quick Actions"
echo "Available management scripts:"
if [ -f "smart_install.sh" ]; then
    echo "   • ./smart_install.sh - Smart installation with options"
fi
if [ -f "dev_reset.sh" ]; then
    echo "   • ./dev_reset.sh - Quick development reset"
fi
echo "   • sudo systemctl restart $SERVICE_NAME - Restart service"
echo "   • journalctl -u $SERVICE_NAME -f - View live logs"
if [ -d "$INSTALL_DIR" ]; then
    echo "   • cd $INSTALL_DIR && source venv/bin/activate - Enter Python environment"
fi

echo ""