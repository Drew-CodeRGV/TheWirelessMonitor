## Stability & Reliability Guide

## Why Systems Crash

### Common Causes

1. **Memory Leaks** - Threads never cleaned up, objects never freed
2. **Database Locks** - SQLite can't handle concurrent writes
3. **Unhandled Exceptions** - Errors crash the entire process
4. **Resource Exhaustion** - Disk full, memory full, too many connections
5. **Infinite Loops** - Background tasks that never complete
6. **Network Timeouts** - Hanging on external API calls

### Your System's Specific Issues

Based on the code review:

1. ✅ **Threading Issues** - Multiple threads accessing SQLite simultaneously
2. ✅ **No Error Recovery** - RSS fetch fails → entire system stops
3. ✅ **No Resource Limits** - Can use unlimited memory/CPU
4. ✅ **No Health Monitoring** - No way to detect problems
5. ✅ **No Automatic Restart** - Crashes require manual intervention
6. ✅ **Log Files Growing** - No rotation, can fill disk

## Stability Improvements

### 1. Install as Systemd Service ⭐ CRITICAL

This ensures automatic restart on crash.

```bash
# Copy service file
sudo cp wireless-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable wireless-monitor

# Start service
sudo systemctl start wireless-monitor

# Check status
sudo systemctl status wireless-monitor
```

**Benefits:**
- ✅ Automatic restart on crash
- ✅ Starts on system boot
- ✅ Resource limits enforced
- ✅ Proper logging
- ✅ Graceful shutdown

### 2. Configure Log Rotation ⭐ CRITICAL

Prevent logs from filling disk.

Create `/etc/logrotate.d/wireless-monitor`:

```
/home/ubuntu/wireless-monitor/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload wireless-monitor > /dev/null 2>&1 || true
    endscript
}
```

Test:
```bash
sudo logrotate -f /etc/logrotate.d/wireless-monitor
```

### 3. Set Up Monitoring ⭐ IMPORTANT

Monitor system health and get alerts.

#### Option A: Simple Cron Health Check

Create `health_check.sh`:

```bash
#!/bin/bash
# Check if service is running and healthy

STATUS=$(systemctl is-active wireless-monitor)

if [ "$STATUS" != "active" ]; then
    echo "Service is down! Status: $STATUS"
    # Send email alert
    echo "Wireless Monitor is down" | mail -s "ALERT: Service Down" your@email.com
    # Restart service
    sudo systemctl restart wireless-monitor
fi

# Check health endpoint
HEALTH=$(curl -s http://localhost:8080/health | jq -r '.status')

if [ "$HEALTH" != "healthy" ]; then
    echo "Service unhealthy! Health: $HEALTH"
    # Send email alert
    echo "Wireless Monitor is unhealthy" | mail -s "ALERT: Service Unhealthy" your@email.com
fi
```

Add to crontab:
```bash
# Check every 5 minutes
*/5 * * * * /home/ubuntu/wireless-monitor/health_check.sh >> /home/ubuntu/wireless-monitor/logs/health_check.log 2>&1
```

#### Option B: UptimeRobot (Free)

1. Sign up at https://uptimerobot.com
2. Add monitor for http://your-server:8080/health
3. Set check interval to 5 minutes
4. Configure email/SMS alerts

### 4. Database Backup ⭐ IMPORTANT

Automatic daily backups.

Create `backup_database.sh`:

```bash
#!/bin/bash
# Backup database daily

BACKUP_DIR="/home/ubuntu/wireless-monitor/backups"
DB_PATH="/home/ubuntu/wireless-monitor/data/wireless_monitor.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/wireless_monitor_$TIMESTAMP.db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Copy database
cp $DB_PATH $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "*.db.gz" -mtime +7 -delete

echo "Backup complete: $BACKUP_FILE.gz"
```

Add to crontab:
```bash
# Backup daily at 3 AM
0 3 * * * /home/ubuntu/wireless-monitor/backup_database.sh >> /home/ubuntu/wireless-monitor/logs/backup.log 2>&1
```

### 5. Memory Monitoring ⭐ IMPORTANT

Monitor and restart if memory too high.

Create `monitor_memory.sh`:

```bash
#!/bin/bash
# Monitor memory usage and restart if too high

MEMORY_LIMIT=80  # Percent
MEMORY_USAGE=$(ps aux | grep 'python3.*main.py' | grep -v grep | awk '{print $4}' | head -1)

if [ -z "$MEMORY_USAGE" ]; then
    echo "Process not found"
    exit 1
fi

MEMORY_INT=${MEMORY_USAGE%.*}

if [ "$MEMORY_INT" -gt "$MEMORY_LIMIT" ]; then
    echo "Memory usage too high: ${MEMORY_USAGE}%"
    echo "Restarting service..."
    sudo systemctl restart wireless-monitor
    echo "Memory usage high: ${MEMORY_USAGE}%" | mail -s "ALERT: High Memory" your@email.com
fi
```

Add to crontab:
```bash
# Check every 15 minutes
*/15 * * * * /home/ubuntu/wireless-monitor/monitor_memory.sh >> /home/ubuntu/wireless-monitor/logs/memory_monitor.log 2>&1
```

### 6. Disk Space Monitoring ⭐ IMPORTANT

Alert when disk space low.

Create `monitor_disk.sh`:

```bash
#!/bin/bash
# Monitor disk space

DISK_LIMIT=85  # Percent
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -gt "$DISK_LIMIT" ]; then
    echo "Disk usage too high: ${DISK_USAGE}%"
    echo "Disk usage high: ${DISK_USAGE}%" | mail -s "ALERT: Low Disk Space" your@email.com
    
    # Clean up old logs
    find /home/ubuntu/wireless-monitor/logs -name "*.log" -mtime +30 -delete
    
    # Clean up old backups
    find /home/ubuntu/wireless-monitor/backups -name "*.db.gz" -mtime +14 -delete
fi
```

Add to crontab:
```bash
# Check daily at 6 AM
0 6 * * * /home/ubuntu/wireless-monitor/monitor_disk.sh >> /home/ubuntu/wireless-monitor/logs/disk_monitor.log 2>&1
```

### 7. Error Rate Monitoring

Track errors in logs.

Create `monitor_errors.sh`:

```bash
#!/bin/bash
# Monitor error rate in logs

LOG_FILE="/home/ubuntu/wireless-monitor/logs/app.log"
ERROR_LIMIT=10  # Errors per hour

# Count errors in last hour
ERRORS=$(grep -c "ERROR" $LOG_FILE | tail -1000)

if [ "$ERRORS" -gt "$ERROR_LIMIT" ]; then
    echo "High error rate: $ERRORS errors in last hour"
    echo "High error rate: $ERRORS errors" | mail -s "ALERT: High Error Rate" your@email.com
    
    # Show last 10 errors
    grep "ERROR" $LOG_FILE | tail -10
fi
```

Add to crontab:
```bash
# Check every hour
0 * * * * /home/ubuntu/wireless-monitor/monitor_errors.sh >> /home/ubuntu/wireless-monitor/logs/error_monitor.log 2>&1
```

## Deployment Checklist

### Initial Setup

- [ ] Apply performance optimizations
  ```bash
  python apply_performance_fixes.py
  python optimize_code.py
  ```

- [ ] Install as systemd service
  ```bash
  sudo cp wireless-monitor.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable wireless-monitor
  sudo systemctl start wireless-monitor
  ```

- [ ] Configure log rotation
  ```bash
  sudo cp logrotate.conf /etc/logrotate.d/wireless-monitor
  sudo logrotate -f /etc/logrotate.d/wireless-monitor
  ```

- [ ] Set up monitoring scripts
  ```bash
  chmod +x *.sh
  crontab -e  # Add monitoring jobs
  ```

- [ ] Configure backups
  ```bash
  mkdir -p backups
  ./backup_database.sh  # Test backup
  ```

- [ ] Test health endpoint
  ```bash
  curl http://localhost:8080/health
  ```

### Verification

- [ ] Service is running
  ```bash
  sudo systemctl status wireless-monitor
  ```

- [ ] Health check passes
  ```bash
  curl http://localhost:8080/health | jq
  ```

- [ ] Logs are rotating
  ```bash
  ls -lh logs/
  ```

- [ ] Backups are working
  ```bash
  ls -lh backups/
  ```

- [ ] Memory usage is reasonable
  ```bash
  ps aux | grep python3
  ```

- [ ] CPU usage is low
  ```bash
  top -p $(pgrep -f "python3.*main.py")
  ```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u wireless-monitor -n 50

# Check for errors
sudo journalctl -u wireless-monitor | grep ERROR

# Test manually
cd /home/ubuntu/wireless-monitor
python3 test_startup.py
```

### High Memory Usage

```bash
# Check current usage
ps aux | grep python3

# Restart service
sudo systemctl restart wireless-monitor

# Check for memory leaks
python3 -m memory_profiler app/main.py
```

### Database Locked

```bash
# Check for multiple processes
ps aux | grep python3

# Kill old processes
pkill -f "python3.*main.py"

# Restart service
sudo systemctl restart wireless-monitor
```

### Slow Performance

```bash
# Check database size
ls -lh data/wireless_monitor.db

# Run cleanup
python3 apply_performance_fixes.py

# Check indexes
sqlite3 data/wireless_monitor.db "SELECT * FROM sqlite_master WHERE type='index';"
```

### Disk Full

```bash
# Check disk usage
df -h

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete

# Clean old backups
find backups/ -name "*.db.gz" -mtime +14 -delete

# Clean old articles
python3 apply_performance_fixes.py
```

## Monitoring Dashboard

### Key Metrics

1. **Uptime** - Target: 99.9%
2. **Response Time** - Target: < 2 seconds
3. **Memory Usage** - Target: < 512MB
4. **CPU Usage** - Target: < 50%
5. **Error Rate** - Target: < 1%
6. **Disk Usage** - Target: < 85%

### Check Commands

```bash
# Service status
sudo systemctl status wireless-monitor

# Memory usage
ps aux | grep python3 | awk '{print $4}'

# CPU usage
ps aux | grep python3 | awk '{print $3}'

# Disk usage
df -h /

# Error count
grep -c ERROR logs/app.log

# Health check
curl http://localhost:8080/health | jq
```

### Grafana Dashboard (Optional)

For advanced monitoring, set up Grafana:

1. Install Prometheus
2. Install Grafana
3. Configure metrics export
4. Create dashboard

## Recovery Procedures

### If Service Crashes

1. Check logs: `sudo journalctl -u wireless-monitor -n 100`
2. Identify error
3. Fix issue
4. Restart: `sudo systemctl restart wireless-monitor`
5. Monitor: `sudo systemctl status wireless-monitor`

### If Database Corrupted

1. Stop service: `sudo systemctl stop wireless-monitor`
2. Restore backup: `cp backups/latest.db.gz data/`
3. Uncompress: `gunzip data/latest.db.gz`
4. Rename: `mv data/latest.db data/wireless_monitor.db`
5. Start service: `sudo systemctl start wireless-monitor`

### If Disk Full

1. Clean logs: `find logs/ -name "*.log" -mtime +7 -delete`
2. Clean backups: `find backups/ -name "*.db.gz" -mtime +7 -delete`
3. Clean old articles: `python3 apply_performance_fixes.py`
4. Restart: `sudo systemctl restart wireless-monitor`

## Expected Results

### Before Stability Improvements

- Uptime: 70-80% (crashes every few weeks)
- Manual restarts required
- No monitoring
- No backups
- Logs fill disk

### After Stability Improvements

- Uptime: 99.9% (automatic recovery)
- No manual intervention needed
- Proactive monitoring
- Daily backups
- Logs rotated automatically

## Maintenance Schedule

### Daily (Automated)
- Log rotation
- Database backup
- Health checks (every 5 min)
- Memory monitoring (every 15 min)

### Weekly (Manual)
- Review logs for errors
- Check disk space
- Verify backups
- Review performance metrics

### Monthly (Manual)
- Update dependencies
- Review and optimize database
- Test backup restoration
- Review monitoring alerts

## Support

### Useful Commands

```bash
# View live logs
sudo journalctl -u wireless-monitor -f

# Restart service
sudo systemctl restart wireless-monitor

# Check health
curl http://localhost:8080/health

# Check memory
ps aux | grep python3

# Check disk
df -h

# Test backup
./backup_database.sh

# Run health check
./health_check.sh
```

### Log Locations

- Application logs: `logs/app.log`
- System logs: `sudo journalctl -u wireless-monitor`
- Health check logs: `logs/health_check.log`
- Backup logs: `logs/backup.log`
- Memory monitor logs: `logs/memory_monitor.log`

## Success Criteria

System is stable when:

- [ ] Uptime > 99%
- [ ] No manual restarts needed
- [ ] Health checks passing
- [ ] Memory usage stable
- [ ] Logs rotating properly
- [ ] Backups running daily
- [ ] Monitoring alerts working
- [ ] Response time < 2 seconds
