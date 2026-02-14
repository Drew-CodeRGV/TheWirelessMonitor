# Deployment and Merge Guide

## Overview

This guide walks through deploying all desktop changes to Raspberry Pi and merging the feature/enhancements branch into main.

## Current Status

- **Current Branch**: feature/enhancements
- **Desktop Status**: All features working and tested
- **Remote Status**: feature/enhancements pushed to origin
- **Main Branch**: Behind by 4 commits

## Pre-Deployment Checklist

### Desktop Verification
- [x] All features tested and working
- [x] Newsletter monitor running successfully
- [x] Web app accessible on http://localhost:8080
- [x] Code committed to feature/enhancements
- [x] Code pushed to GitHub

### Files to Transfer Separately (NOT in Git)
- `credentials.json` - Gmail OAuth credentials
- `token.json` - Gmail access token (auto-generated)
- `.env` - Environment variables (if you created one)
- `data/wireless_monitor.db` - Database (optional - can start fresh on Pi)

## Step 1: Merge to Main Branch (Desktop)

### 1.1 Ensure Everything is Committed
```bash
# Check for uncommitted changes
git status

# If logs/app.log is modified, you can ignore it or add to .gitignore
echo "logs/*.log" >> .gitignore
git add .gitignore
git commit -m "Ignore log files"
git push origin feature/enhancements
```

### 1.2 Switch to Main and Merge
```bash
# Switch to main branch
git checkout main

# Pull latest changes (if any)
git pull origin main

# Merge feature/enhancements into main
git merge feature/enhancements

# Push merged main to GitHub
git push origin main
```

### 1.3 Verify Merge
```bash
# Check that main is up to date
git log --oneline -5

# Verify all files are present
git status
```

## Step 2: Raspberry Pi Deployment

### 2.1 SSH to Raspberry Pi
```bash
ssh pi@<raspberry-pi-ip-address>
# Or if you have a hostname configured:
ssh pi@raspberrypi.local
```

### 2.2 Navigate to Project Directory
```bash
cd /home/pi/wireless-monitor
# Or wherever your project is located
```

### 2.3 Pull Latest Code from Main
```bash
# Ensure you're on main branch
git checkout main

# Pull latest changes
git pull origin main

# Verify you got all the updates
git log --oneline -5
```

### 2.4 Install New Dependencies
```bash
# Install Python dependencies
pip3 install --upgrade -r requirements.txt

# Specifically for newsletter monitoring:
pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client beautifulsoup4

# For DuckDuckGo search (Wild Wi-Fi):
pip3 install duckduckgo-search

# Verify installations
pip3 list | grep -E "google-auth|google-api|duckduckgo"
```

### 2.5 Transfer Credentials Files

**From Desktop (Windows PowerShell):**
```powershell
# Transfer credentials.json
scp credentials.json pi@<raspberry-pi-ip>:/home/pi/wireless-monitor/

# Transfer token.json
scp token.json pi@<raspberry-pi-ip>:/home/pi/wireless-monitor/
```

**On Raspberry Pi:**
```bash
# Set proper permissions
chmod 600 credentials.json token.json

# Verify files exist
ls -la credentials.json token.json
```

### 2.6 Update Environment Variables (if needed)
```bash
# If you have a .env file, create it on Pi
nano .env

# Add any necessary environment variables:
# ELEVENLABS_API_KEY=your_key_here
# ELEVENLABS_VOICE_ID=your_voice_id_here
# etc.

# Save and exit (Ctrl+X, Y, Enter)
chmod 600 .env
```

### 2.7 Install/Update Systemd Services

**Main Wireless Monitor Service:**
```bash
# Copy service file
sudo cp systemd/wireless-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable wireless-monitor.service

# Restart service with new code
sudo systemctl restart wireless-monitor.service

# Check status
sudo systemctl status wireless-monitor.service
```

**Newsletter Monitor Service:**
```bash
# Copy service file
sudo cp systemd/newsletter-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable newsletter-monitor.service

# Start service
sudo systemctl start newsletter-monitor.service

# Check status
sudo systemctl status newsletter-monitor.service
```

### 2.8 Verify Services are Running
```bash
# Check wireless-monitor
sudo systemctl status wireless-monitor.service

# Check newsletter-monitor
sudo systemctl status newsletter-monitor.service

# View logs
sudo journalctl -u wireless-monitor.service -f
sudo journalctl -u newsletter-monitor.service -f
```

### 2.9 Test Web Interface
```bash
# From Pi, test locally
curl http://localhost:5000

# From desktop, test remotely
# Open browser to: http://<raspberry-pi-ip>:5000
```

## Step 3: Verification and Testing

### 3.1 Verify All Features Work on Pi

**RSS Feed Fetching:**
- Visit http://<pi-ip>:5000/admin
- Click "Fetch Now" button
- Verify articles are fetched

**Newsletter Monitoring:**
- Check newsletter monitor logs: `sudo journalctl -u newsletter-monitor.service -n 50`
- Send a test newsletter to wifinewsletters@gmail.com
- Wait 10 minutes and verify it's processed

**Wild Wi-Fi Stories:**
- Visit http://<pi-ip>:5000/wild_wifi
- Click "Search for New Stories" button
- Verify stories are found and displayed

**Reader View:**
- Visit http://<pi-ip>:5000
- Toggle Reader Mode
- Test sort by Date and Score buttons

**ElevenLabs Podcast:**
- Visit http://<pi-ip>:5000/weekly_digest
- Click "Generate Podcast" button
- Verify audio is generated (if API key has permissions)

### 3.2 Monitor System Resources
```bash
# Check memory usage
free -h

# Check CPU usage
top

# Check disk space
df -h

# Check service resource usage
systemctl status wireless-monitor.service
systemctl status newsletter-monitor.service
```

## Step 4: Cleanup (Optional)

### 4.1 Delete Feature Branch (if desired)
```bash
# On desktop, after successful merge and deployment:
git branch -d feature/enhancements

# Delete remote branch
git push origin --delete feature/enhancements
```

### 4.2 Clean Up Desktop
```bash
# Switch back to main on desktop
git checkout main
git pull origin main
```

## Troubleshooting

### Service Won't Start
```bash
# Check service logs
sudo journalctl -u wireless-monitor.service -n 100
sudo journalctl -u newsletter-monitor.service -n 100

# Check for Python errors
python3 app/main.py
python3 gmail_api_newsletter_monitor.py --mode once
```

### Newsletter Monitor Authentication Issues
```bash
# Re-authenticate (will open browser)
python3 gmail_api_newsletter_monitor.py --mode once

# If running headless, authenticate on desktop first, then transfer token.json
```

### Port Already in Use
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>

# Restart service
sudo systemctl restart wireless-monitor.service
```

### Database Issues
```bash
# Check database exists
ls -la data/wireless_monitor.db

# Check database permissions
chmod 644 data/wireless_monitor.db

# If corrupted, restore from backup or start fresh
mv data/wireless_monitor.db data/wireless_monitor.db.backup
python3 app/main.py  # Will create new database
```

## Post-Deployment Checklist

- [ ] Main branch merged and pushed
- [ ] Code deployed to Raspberry Pi
- [ ] All dependencies installed
- [ ] Credentials transferred and secured
- [ ] Both systemd services running
- [ ] Web interface accessible
- [ ] RSS feeds fetching successfully
- [ ] Newsletter monitor working
- [ ] Wild Wi-Fi search functional
- [ ] Reader view working
- [ ] All features tested on Pi

## Rollback Plan (if needed)

If something goes wrong:

```bash
# On Raspberry Pi
git log --oneline -10
git checkout <previous-commit-hash>
sudo systemctl restart wireless-monitor.service
sudo systemctl restart newsletter-monitor.service
```

## Success Criteria

✅ Main branch contains all features
✅ Raspberry Pi running latest code
✅ Both services auto-start on boot
✅ Web interface accessible remotely
✅ All features working as expected
✅ System stable and performant

## Next Steps

After successful deployment:
1. Monitor system for 24 hours
2. Check logs for any errors
3. Verify scheduled tasks run correctly
4. Set up automated backups (optional)
5. Configure firewall rules (optional)
6. Set up SSL/HTTPS (optional)

## Support

If you encounter issues:
1. Check service logs: `sudo journalctl -u <service-name> -n 100`
2. Check application logs: `tail -f logs/app.log`
3. Verify network connectivity
4. Ensure all dependencies are installed
5. Check file permissions

---

**Created**: 2026-02-14
**Last Updated**: 2026-02-14
**Status**: Ready for deployment
