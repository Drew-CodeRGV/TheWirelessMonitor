#!/bin/bash

# RSS News Aggregator System Monitor
# Checks system health and restarts services if needed

INSTALL_DIR="/home/wifi/rss_aggregator"
LOG_FILE="$INSTALL_DIR/logs/monitor.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo -e "$1"
}

check_service() {
    local service_name=$1
    if systemctl is-active --quiet "$service_name"; then
        log_message "${GREEN}✓${NC} $service_name is running"
        return 0
    else
        log_message "${RED}✗${NC} $service_name is not running"
        return 1
    fi
}

restart_service() {
    local service_name=$1
    log_message "${YELLOW}⟳${NC} Restarting $service_name..."
    sudo systemctl restart "$service_name"
    sleep 5
    if check_service "$service_name"; then
        log_message "${GREEN}✓${NC} $service_name restarted successfully"
    else
        log_message "${RED}✗${NC} Failed to restart $service_name"
    fi
}

check_web_interface() {
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200"; then
        log_message "${GREEN}✓${NC} Web interface is responding"
        return 0
    else
        log_message "${RED}✗${NC} Web interface is not responding"
        return 1
    fi
}

check_ollama() {
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_message "${GREEN}✓${NC} Ollama is responding"
        return 0
    else
        log_message "${RED}✗${NC} Ollama is not responding"
        return 1
    fi
}

check_database() {
    if [ -f "$INSTALL_DIR/data/news.db" ]; then
        if sqlite3 "$INSTALL_DIR/data/news.db" "SELECT COUNT(*) FROM rss_feeds;" > /dev/null 2>&1; then
            log_message "${GREEN}✓${NC} Database is accessible"
            return 0
        else
            log_message "${RED}✗${NC} Database is corrupted"
            return 1
        fi
    else
        log_message "${RED}✗${NC} Database file not found"
        return 1
    fi
}

check_disk_space() {
    local usage=$(df "$INSTALL_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -lt 90 ]; then
        log_message "${GREEN}✓${NC} Disk usage: ${usage}%"
        return 0
    else
        log_message "${YELLOW}⚠${NC} Disk usage high: ${usage}%"
        return 1
    fi
}

main() {
    log_message "=== RSS News Aggregator Health Check ==="
    
    # Check services
    services=("rss-aggregator" "nginx" "ollama")
    for service in "${services[@]}"; do
        if ! check_service "$service"; then
            restart_service "$service"
        fi
    done
    
    # Check web interface
    if ! check_web_interface; then
        restart_service "rss-aggregator"
        sleep 10
        check_web_interface
    fi
    
    # Check Ollama
    if ! check_ollama; then
        restart_service "ollama"
        sleep 15
        check_ollama
    fi
    
    # Check database
    check_database
    
    # Check disk space
    check_disk_space
    
    # Clean old logs (keep last 30 days)
    find "$INSTALL_DIR/logs" -name "*.log" -mtime +30 -delete 2>/dev/null
    
    log_message "=== Health check completed ==="
    echo ""
}

# Create log directory if it doesn't exist
mkdir -p "$INSTALL_DIR/logs"

# Run main function
main