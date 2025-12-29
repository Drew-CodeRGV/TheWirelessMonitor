# Deployment Guide for The Wireless Monitor

## Pre-Deployment Checklist

### 1. Repository Setup
- [ ] Create GitHub repository: `TheWirelessMonitor`
- [ ] Upload all project files
- [ ] Repository URL: https://github.com/Drew-CodeRGV/TheWirelessMonitor
- [ ] Test installation script on clean Raspberry Pi

### 2. Raspberry Pi Preparation
- [ ] Fresh Raspberry Pi OS installation
- [ ] SSH enabled (if deploying remotely)
- [ ] Internet connection configured
- [ ] At least 2GB free space available

## Deployment Steps

## Deployment Steps

### Option A: Universal Installation (Works with Any User)
**Recommended**: This works on any Linux system or macOS with any username:

```bash
# Works with any user on Linux or macOS
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/universal_install.sh | bash
```

### Option B: Raspberry Pi Installation (Requires 'pi' user)
**Traditional**: This is the original Raspberry Pi specific installation:

```bash
# Only works with 'pi' user on Raspberry Pi
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/scripts/install.sh | bash
```

### Option C: Bootstrap Installation (Repository Doesn't Exist Yet)
If you're getting a 404 error, use this bootstrap method:

```bash
# This prepares the system and installs dependencies
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/bootstrap_install.sh | bash
```

Then follow the steps to create the repository and upload files.

### Option C: Manual Installation
For complete manual control:

```bash
# 1. Prepare system
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl wget sqlite3 nginx

# 2. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
ollama pull llama2:7b-chat

# 3. Create directory
sudo mkdir -p /home/pi/rss_aggregator
sudo chown pi:pi /home/pi/rss_aggregator
cd /home/pi/rss_aggregator

# 4. Copy project files manually or clone when repository exists
# git clone https://github.com/Drew-CodeRGV/TheWirelessMonitor.git .

# 5. Continue with Python setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Initialize database
python3 -c "from app.models import init_db; init_db()"

# 7. Set up services (see full install.sh for complete steps)
```

### Step 2: Verify Installation
```bash
# Check services are running
sudo systemctl status rss-aggregator
sudo systemctl status nginx
sudo systemctl status ollama

# Check web interface
curl -I http://localhost
```

### Step 3: Initial Configuration
1. Open web browser to `http://your-pi-ip`
2. Navigate to "Manage Feeds"
3. Verify default feeds are loaded
4. Add any additional RSS feeds
5. Click "Fetch Now" to test

### Step 4: Verify Automation
```bash
# Check cron jobs
crontab -l

# Test manual fetch
cd /home/pi/rss_aggregator
source venv/bin/activate
python scripts/daily_fetch.py
```

## Post-Deployment Configuration

### Custom RSS Feeds
Add industry-specific feeds through the web interface:
- Fierce Wireless: `https://www.fiercewireless.com/rss/xml`
- Mobile World Live: `https://www.mobileworldlive.com/feed/`
- Network World: `https://www.networkworld.com/index.rss`

### AI Model Optimization
```bash
# Switch to a lighter model if needed
ollama pull llama2:7b-chat-q4_0  # Quantized version
```

### Performance Tuning
Edit `/home/pi/rss_aggregator/config/settings.py`:
```python
# Reduce fetch frequency for slower Pi
RSS_FETCH_INTERVAL = timedelta(hours=12)

# Limit articles per feed
MAX_ARTICLES_PER_FEED = 25

# Reduce AI timeout
AI_ANALYSIS_TIMEOUT = 30
```

## Monitoring and Maintenance

### Health Monitoring
```bash
# Add monitor script to cron
(crontab -l; echo "*/15 * * * * /home/pi/rss_aggregator/scripts/monitor.sh") | crontab -
```

### Log Management
```bash
# View application logs
journalctl -u rss-aggregator -f

# View cron logs
tail -f /home/pi/rss_aggregator/logs/cron.log

# View monitor logs
tail -f /home/pi/rss_aggregator/logs/monitor.log
```

### Updates
```bash
# Update system
cd /home/pi/rss_aggregator
./update.sh
```

## Troubleshooting

### Common Issues

**Web interface not loading:**
```bash
sudo systemctl restart nginx
sudo systemctl restart rss-aggregator
```

**AI analysis not working:**
```bash
sudo systemctl restart ollama
ollama list  # Check if model is installed
```

**Database errors:**
```bash
cd /home/pi/rss_aggregator
python3 -c "from app.models import init_db; init_db()"
```

**High CPU usage:**
- Reduce fetch frequency
- Use lighter AI model
- Limit concurrent processing

### Performance Optimization

**For Raspberry Pi 3:**
- Use `llama2:7b-chat-q4_0` model
- Increase fetch interval to 12 hours
- Reduce max articles per feed to 20

**For Raspberry Pi 4:**
- Default settings should work well
- Consider `llama2:13b-chat` for better analysis

## Security Hardening

### Basic Security
```bash
# Change default SSH password
passwd

# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall (optional)
sudo ufw enable
sudo ufw allow 22  # SSH
sudo ufw allow 80  # HTTP
```

### Application Security
1. Change secret key in settings
2. Consider HTTPS setup with Let's Encrypt
3. Regularly update dependencies
4. Monitor access logs

## Backup Strategy

### Database Backup
```bash
# Create backup script
cat > /home/pi/backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /home/pi/rss_aggregator/data/news.db /home/pi/backups/news_${DATE}.db
find /home/pi/backups -name "news_*.db" -mtime +7 -delete
EOF

chmod +x /home/pi/backup_db.sh

# Add to cron
(crontab -l; echo "0 2 * * * /home/pi/backup_db.sh") | crontab -
```

## Production Checklist

- [ ] Installation completed successfully
- [ ] Web interface accessible
- [ ] RSS feeds configured and fetching
- [ ] AI analysis working
- [ ] Cron jobs scheduled
- [ ] Services auto-start on boot
- [ ] Monitoring script active
- [ ] Backup strategy implemented
- [ ] Documentation updated with your specific URLs
- [ ] Performance optimized for your Pi model

## Support

For issues:
1. Check system logs
2. Run monitor script
3. Review troubleshooting section
4. Check GitHub issues
5. Verify Pi meets minimum requirements

---

**Remember to:**
- Test thoroughly before production deployment
- Keep system updated regularly
- Monitor resource usage
- The repository is now live at https://github.com/Drew-CodeRGV/TheWirelessMonitor