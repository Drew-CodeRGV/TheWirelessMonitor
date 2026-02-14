# Quick Deployment Steps

## TL;DR - Fast Track

### On Desktop (Windows)

```powershell
# 1. Merge to main
.\merge_to_main.ps1

# 2. Transfer credentials to Pi
scp credentials.json pi@<pi-ip>:/home/pi/wireless-monitor/
scp token.json pi@<pi-ip>:/home/pi/wireless-monitor/
```

### On Raspberry Pi

```bash
# 1. SSH to Pi
ssh pi@<pi-ip>

# 2. Navigate to project
cd /home/pi/wireless-monitor

# 3. Run deployment script
chmod +x deploy_to_pi_complete.sh
./deploy_to_pi_complete.sh

# 4. Verify
curl http://localhost:5000
```

Done! 🎉

---

## Detailed Steps

### Phase 1: Desktop Merge (5 minutes)

1. **Run merge script:**
   ```powershell
   .\merge_to_main.ps1
   ```
   
2. **Verify merge:**
   ```powershell
   git log --oneline -5
   ```

### Phase 2: Transfer Files (2 minutes)

1. **Transfer credentials:**
   ```powershell
   scp credentials.json pi@<pi-ip>:/home/pi/wireless-monitor/
   scp token.json pi@<pi-ip>:/home/pi/wireless-monitor/
   ```

### Phase 3: Pi Deployment (10 minutes)

1. **SSH to Pi:**
   ```bash
   ssh pi@<pi-ip>
   ```

2. **Deploy:**
   ```bash
   cd /home/pi/wireless-monitor
   chmod +x deploy_to_pi_complete.sh
   ./deploy_to_pi_complete.sh
   ```

3. **Test:**
   - Open browser: `http://<pi-ip>:5000`
   - Check all features work

---

## Verification Checklist

- [ ] Main branch merged and pushed
- [ ] Credentials transferred to Pi
- [ ] Code pulled on Pi
- [ ] Dependencies installed
- [ ] Services running
- [ ] Web interface accessible
- [ ] RSS feeds working
- [ ] Newsletter monitor active
- [ ] Wild Wi-Fi search functional
- [ ] Reader view working

---

## Quick Commands

### Check Service Status
```bash
sudo systemctl status wireless-monitor.service
sudo systemctl status newsletter-monitor.service
```

### View Logs
```bash
sudo journalctl -u wireless-monitor.service -f
sudo journalctl -u newsletter-monitor.service -f
tail -f logs/app.log
```

### Restart Services
```bash
sudo systemctl restart wireless-monitor.service
sudo systemctl restart newsletter-monitor.service
```

### Test Endpoints
```bash
curl http://localhost:5000
curl http://localhost:5000/admin
curl http://localhost:5000/wild_wifi
```

---

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u wireless-monitor.service -n 50
python3 app/main.py  # Test manually
```

### Port in use
```bash
sudo lsof -i :5000
sudo kill -9 <PID>
sudo systemctl restart wireless-monitor.service
```

### Newsletter auth issues
```bash
python3 gmail_api_newsletter_monitor.py --mode once
```

---

## Success Indicators

✅ Both services show "active (running)"
✅ Web interface loads without errors
✅ Articles are being fetched
✅ Newsletter monitor checking every 10 minutes
✅ Wild Wi-Fi stories can be searched
✅ Reader view toggles correctly

---

**Total Time**: ~15-20 minutes
**Difficulty**: Easy (automated scripts)
**Risk**: Low (can rollback if needed)
