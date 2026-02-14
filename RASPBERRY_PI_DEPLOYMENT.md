# Raspberry Pi Deployment Guide

## Overview
Deploy the Wireless Monitor with newsletter monitoring to your Raspberry Pi for 24/7 autonomous operation.

## Pre-Deployment Checklist (On Desktop)

### 1. Commit Code Changes
```bash
git status
git add .
git commit -m "Add newsletter monitoring and reader sort features"
git push origin main
```

### 2. Backup Credentials (DO NOT COMMIT!)
Save these files separately - they contain secrets:
- `credentials.json` - Gmail OAuth credentials
- `token.json` - Gmail access token
- `.env` - Environment variables (if you created one)

**Copy these to a secure location** (USB drive, encrypted folder, password manager)

### 3. Note Your Configuration
- Gmail account: wifinewsletters@gmail.com
- Check interval: 10 minutes (or your preference)
- Database location: data/wireless_monitor.db

## Raspberry Pi Setup

### Step 1: Pull Latest Code

SSH into your Raspberry Pi:
```bash
ssh pi@your-pi-address
```

Navigate to your project:
```bash
cd /path/to/WirelessSignal
```

Pull latest changes:
```bash
git pull origin main
```

### Step 2: Install New Dependencies

```bash
# Activate virtual environment if you have one
source venv/bin/activate

# Install Gmail API packages
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Install BeautifulSoup if not already installed
pip install beautifulsoup4
```

### Step 3: Transfer Credentials

**Option A: SCP from Desktop**
```bash
# From your desktop (Windows PowerShell)
scp credentials.json pi@your-pi-address:/path/to/WirelessSignal/
scp token.json pi@your-pi-address:/path/to/WirelessSignal/
```

**Option B: Manual Copy**
1. Copy `credentials.json` and `token.json` to USB drive
2. Insert USB into Pi
3. Copy files:
```bash
cp /media/usb/credentials.json /path/to/WirelessSignal/
cp /media/usb/token.json /path/to/WirelessSignal/
```

**Option C: Recreate on Pi**
If you can't transfer files:
1. Copy content of `credentials.json` from desktop
2. On Pi: `nano credentials.json`
3. Paste content, save (Ctrl+X, Y, Enter)
4. Run newsletter monitor once to generate `token.json`

### Step 4: Set Permissions

```bash
chmod 600 credentials.json token.json
```

### Step 5: Test Newsletter Monitor

```bash
python gmail_api_newsletter_monitor.py
# Select: 1 (one-time check)
```

Should show:
```
✅ Successfully authenticated with Gmail API
Found X unread messages
```

## Autonomous Operation Setup

### Option 1: Systemd Service (Recommended)

Create service file for main app:
```bash
sudo nano /etc/systemd/system/wireless-monitor.service
```

Content:
```ini
[Unit]
Description=Wireless Monitor Web Application
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/WirelessSignal
ExecStart=/usr/bin/python3 /home/pi/WirelessSignal/app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create service for newsletter monitor:
```bash
sudo nano /etc/systemd/system/newsletter-monitor.service
```

Content:
```ini
[Unit]
Description=Gmail Newsletter Monitor
After=network.target wireless-monitor.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/WirelessSignal
ExecStart=/usr/bin/python3 /home/pi/WirelessSignal/gmail_api_newsletter_monitor.py
Restart=always
RestartSec=10
StandardInput=null

[Install]
WantedBy=multi-user.target
```

**Note**: The newsletter monitor needs to run in non-interactive mode. Update the script:

```bash
nano gmail_api_newsletter_monitor.py
```

Change the `main()` function to:
```python
def main():
    """Main function"""
    import sys
    
    # Check if running as service (no terminal)
    if not sys.stdin.isatty():
        # Run in continuous mode automatically
        monitor = GmailAPINewsletterMonitor()
        monitor.run_continuous(interval_minutes=10)
    else:
        # Interactive mode
        print("=" * 60)
        print("Gmail API Newsletter Monitor")
        print("=" * 60)
        # ... rest of interactive code
```

Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable wireless-monitor
sudo systemctl enable newsletter-monitor
sudo systemctl start wireless-monitor
sudo systemctl start newsletter-monitor
```

Check status:
```bash
sudo systemctl status wireless-monitor
sudo systemctl status newsletter-monitor
```

View logs:
```bash
sudo journalctl -u wireless-monitor -f
sudo journalctl -u newsletter-monitor -f
```

### Option 2: Cron Job (Alternative)

Edit crontab:
```bash
crontab -e
```

Add:
```bash
# Start Wireless Monitor on boot
@reboot cd /home/pi/WirelessSignal && python3 app/main.py >> logs/app.log 2>&1 &

# Start Newsletter Monitor on boot
@reboot cd /home/pi/WirelessSignal && python3 gmail_api_newsletter_monitor.py >> logs/newsletter.log 2>&1 &

# Check newsletter every 10 minutes (backup)
*/10 * * * * cd /home/pi/WirelessSignal && python3 -c "from gmail_api_newsletter_monitor import GmailAPINewsletterMonitor; m = GmailAPINewsletterMonitor(); m.fetch_newsletters()" >> logs/newsletter.log 2>&1
```

## Verification

### 1. Check Web Interface
```bash
# From Pi
curl http://localhost:8080

# From desktop browser
http://your-pi-address:8080
```

### 2. Check Newsletter Monitor
```bash
# View logs
tail -f logs/newsletter.log

# Or systemd logs
sudo journalctl -u newsletter-monitor -f
```

### 3. Send Test Newsletter
1. Forward a tech newsletter to wifinewsletters@gmail.com
2. Wait 10 minutes
3. Check logs for "Processing newsletter..."
4. Visit http://your-pi-address:8080
5. Verify articles appear

## Monitoring & Maintenance

### Check Service Status
```bash
sudo systemctl status wireless-monitor
sudo systemctl status newsletter-monitor
```

### Restart Services
```bash
sudo systemctl restart wireless-monitor
sudo systemctl restart newsletter-monitor
```

### View Logs
```bash
# Application logs
tail -f logs/app.log

# Newsletter monitor logs
sudo journalctl -u newsletter-monitor -n 100

# All logs
sudo journalctl -u wireless-monitor -u newsletter-monitor -f
```

### Update Code
```bash
cd /home/pi/WirelessSignal
git pull origin main
sudo systemctl restart wireless-monitor
sudo systemctl restart newsletter-monitor
```

## Troubleshooting

### Newsletter Monitor Not Running
```bash
# Check if process is running
ps aux | grep gmail_api

# Check for errors
sudo journalctl -u newsletter-monitor -n 50

# Test manually
python3 gmail_api_newsletter_monitor.py
```

### Token Expired
```bash
# Delete old token
rm token.json

# Run manually to re-authenticate
python3 gmail_api_newsletter_monitor.py
# This will open browser for re-auth

# Or regenerate on desktop and transfer
```

### Credentials Missing
```bash
# Check files exist
ls -la credentials.json token.json

# Check permissions
chmod 600 credentials.json token.json

# Verify content
head -n 5 credentials.json
```

### No Articles Appearing
```bash
# Check database
sqlite3 data/wireless_monitor.db "SELECT COUNT(*) FROM articles;"

# Check newsletter feeds
sqlite3 data/wireless_monitor.db "SELECT * FROM rss_feeds WHERE url LIKE '%@%';"

# Check logs for errors
sudo journalctl -u newsletter-monitor -n 100 | grep ERROR
```

## Security Best Practices

1. **Credentials Protection**
   - Never commit credentials.json or token.json
   - Set file permissions to 600
   - Store backups securely

2. **Network Security**
   - Use firewall to restrict access
   - Consider VPN for remote access
   - Use HTTPS if exposing to internet

3. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade
   pip install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

4. **Backup**
   ```bash
   # Backup database
   cp data/wireless_monitor.db data/wireless_monitor.db.backup
   
   # Backup credentials
   cp credentials.json token.json /secure/backup/location/
   ```

## Performance Optimization

### Reduce Memory Usage
```bash
# Limit check interval
# Edit newsletter monitor to check every 30 minutes instead of 10
```

### Reduce CPU Usage
```bash
# Lower process priority
sudo systemctl edit newsletter-monitor
```

Add:
```ini
[Service]
Nice=10
```

## File Checklist

Files that MUST be on Pi:
- ✅ All Python scripts (from git)
- ✅ credentials.json (transferred separately)
- ✅ token.json (transferred separately)
- ✅ data/ directory
- ✅ logs/ directory
- ✅ app/ directory with all templates

Files that should NOT be on Pi:
- ❌ .env with passwords (use systemd environment instead)
- ❌ Test files (optional)
- ❌ Documentation .md files (optional)

## Quick Reference Commands

```bash
# Start everything
sudo systemctl start wireless-monitor newsletter-monitor

# Stop everything
sudo systemctl stop wireless-monitor newsletter-monitor

# Restart everything
sudo systemctl restart wireless-monitor newsletter-monitor

# Check status
sudo systemctl status wireless-monitor newsletter-monitor

# View logs
sudo journalctl -u newsletter-monitor -f

# Test newsletter monitor
python3 gmail_api_newsletter_monitor.py

# Check database
sqlite3 data/wireless_monitor.db "SELECT COUNT(*) FROM articles;"

# Update code
git pull && sudo systemctl restart wireless-monitor newsletter-monitor
```

## Success Indicators

✅ Web interface accessible at http://pi-address:8080
✅ Newsletter monitor service running
✅ Logs show "Checking for new newsletters..." every 10 minutes
✅ Articles from newsletters appear in web interface
✅ No errors in systemd logs
✅ Services restart automatically after reboot

## Support

If issues persist:
1. Check all logs
2. Verify credentials are valid
3. Test manually before running as service
4. Check network connectivity
5. Verify Gmail API quota not exceeded
