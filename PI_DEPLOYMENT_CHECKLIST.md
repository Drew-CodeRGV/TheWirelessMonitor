# Raspberry Pi Deployment Checklist

## Pre-Deployment (On Desktop)

### ☐ 1. Save Credentials Securely
- [ ] Copy `credentials.json` to secure location
- [ ] Copy `token.json` to secure location
- [ ] Note: These files are in .gitignore and won't be pushed to GitHub

### ☐ 2. Commit All Code Changes
```bash
git status
git add .
git commit -m "Add newsletter monitoring, reader sort, and Wild Wi-Fi search"
git push origin main
```

### ☐ 3. Verify What's Being Pushed
Check that these are included:
- [ ] `gmail_api_newsletter_monitor.py`
- [ ] `email_newsletter_monitor.py` (backup IMAP version)
- [ ] `systemd/*.service` files
- [ ] `RASPBERRY_PI_DEPLOYMENT.md`
- [ ] Updated `app/main.py` (with sort feature)
- [ ] Updated `app/templates/index.html` (with sort buttons)
- [ ] `.gitignore` (updated to exclude credentials)

Check that these are NOT included:
- [ ] `credentials.json` (should be ignored)
- [ ] `token.json` (should be ignored)
- [ ] `data/*.db` (should be ignored)
- [ ] `logs/*.log` (should be ignored)

## Deployment to Pi

### ☐ 4. SSH to Raspberry Pi
```bash
ssh pi@your-pi-address
cd /home/pi/WirelessSignal
```

### ☐ 5. Pull Latest Code
```bash
git pull origin main
```

### ☐ 6. Install Dependencies
```bash
pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client beautifulsoup4
```

### ☐ 7. Transfer Credentials
**From Desktop (PowerShell):**
```powershell
scp credentials.json pi@your-pi-address:/home/pi/WirelessSignal/
scp token.json pi@your-pi-address:/home/pi/WirelessSignal/
```

**On Pi:**
```bash
chmod 600 credentials.json token.json
ls -la credentials.json token.json
```

### ☐ 8. Test Newsletter Monitor
```bash
python3 gmail_api_newsletter_monitor.py
# Should show: "Running in non-interactive mode" or prompt for mode
# Press Ctrl+C if it starts running
```

### ☐ 9. Install Systemd Services
```bash
sudo cp systemd/wireless-monitor.service /etc/systemd/system/
sudo cp systemd/newsletter-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### ☐ 10. Enable and Start Services
```bash
sudo systemctl enable wireless-monitor
sudo systemctl enable newsletter-monitor
sudo systemctl start wireless-monitor
sudo systemctl start newsletter-monitor
```

### ☐ 11. Verify Services Running
```bash
sudo systemctl status wireless-monitor
sudo systemctl status newsletter-monitor
```

Should show: "active (running)" in green

## Verification

### ☐ 12. Check Web Interface
**From Pi:**
```bash
curl http://localhost:8080
```

**From Desktop Browser:**
```
http://your-pi-address:8080
```

Should see the Wireless Monitor interface

### ☐ 13. Check Newsletter Monitor Logs
```bash
sudo journalctl -u newsletter-monitor -n 50
```

Should see:
- "Successfully authenticated with Gmail API"
- "Starting continuous monitoring"
- "Checking for new newsletters..."

### ☐ 14. Test Newsletter Processing
1. [ ] Forward a tech newsletter to wifinewsletters@gmail.com
2. [ ] Wait 10 minutes
3. [ ] Check logs: `sudo journalctl -u newsletter-monitor -f`
4. [ ] Should see: "Processing newsletter..."
5. [ ] Visit http://your-pi-address:8080
6. [ ] Verify articles appear

### ☐ 15. Test Reader Sort Feature
1. [ ] Go to http://your-pi-address:8080/?view=reader
2. [ ] Click "⭐ Score" button
3. [ ] Click "📅 Date" button
4. [ ] Verify articles re-sort

### ☐ 16. Test Wild Wi-Fi Search
1. [ ] Go to http://your-pi-address:8080/wild_wifi_settings
2. [ ] Click "Search for Stories Now"
3. [ ] Wait for search to complete
4. [ ] Verify stories appear on Wild Wi-Fi page

## Post-Deployment

### ☐ 17. Set Up Monitoring
Add to your monitoring routine:
```bash
# Check services daily
sudo systemctl status wireless-monitor newsletter-monitor

# Check logs weekly
sudo journalctl -u newsletter-monitor -n 100
```

### ☐ 18. Subscribe to Newsletters
Send these to wifinewsletters@gmail.com:
- [ ] TechCrunch Daily
- [ ] The Verge Newsletter
- [ ] Ars Technica
- [ ] IEEE Spectrum
- [ ] Fierce Wireless
- [ ] RCR Wireless News

### ☐ 19. Backup Credentials
Store securely:
- [ ] `credentials.json` - in password manager or encrypted storage
- [ ] `token.json` - in password manager or encrypted storage
- [ ] Note: You'll need these if you rebuild the Pi

### ☐ 20. Document Your Setup
Note for future reference:
- [ ] Pi IP address: _______________
- [ ] Gmail account: wifinewsletters@gmail.com
- [ ] Check interval: 10 minutes
- [ ] Service names: wireless-monitor, newsletter-monitor

## Troubleshooting

### If Services Won't Start
```bash
# Check for errors
sudo journalctl -u newsletter-monitor -n 50

# Test manually
python3 gmail_api_newsletter_monitor.py

# Check credentials
ls -la credentials.json token.json
```

### If No Articles Appearing
```bash
# Check database
sqlite3 data/wireless_monitor.db "SELECT COUNT(*) FROM articles;"

# Check newsletter feeds
sqlite3 data/wireless_monitor.db "SELECT * FROM rss_feeds WHERE url LIKE '%@%';"

# Force a check
sudo systemctl restart newsletter-monitor
sudo journalctl -u newsletter-monitor -f
```

### If Token Expired
```bash
# Delete token
rm token.json

# Run manually to re-authenticate
python3 gmail_api_newsletter_monitor.py
# This will open browser for re-auth

# Copy new token.json back to desktop for backup
```

## Success Criteria

✅ All services running
✅ Web interface accessible
✅ Newsletter monitor checking every 10 minutes
✅ Articles from newsletters appearing
✅ Reader sort feature working
✅ Wild Wi-Fi search working
✅ No errors in logs
✅ Services restart after reboot

## Quick Commands Reference

```bash
# Restart everything
sudo systemctl restart wireless-monitor newsletter-monitor

# View logs
sudo journalctl -u newsletter-monitor -f

# Update code
cd /home/pi/WirelessSignal && git pull && sudo systemctl restart wireless-monitor newsletter-monitor

# Check status
sudo systemctl status wireless-monitor newsletter-monitor

# Stop everything
sudo systemctl stop wireless-monitor newsletter-monitor
```

## Notes

- Newsletter monitor runs automatically in non-interactive mode
- Checks every 10 minutes for new newsletters
- Credentials are secure (600 permissions, not in git)
- Services auto-restart on failure
- Services auto-start on boot
- Logs available via journalctl

## Completion

Date deployed: _______________
Deployed by: _______________
Pi address: _______________
Status: ☐ Complete ☐ Issues (describe below)

Issues/Notes:
_________________________________
_________________________________
_________________________________
