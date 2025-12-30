# Installation Guide - The Wireless Monitor Streamlined Edition

## 🚀 Quick Installation

### One-Command Install
```bash
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/install.sh | bash
```

### Manual Installation
```bash
# 1. Clone repository
git clone https://github.com/Drew-CodeRGV/TheWirelessMonitor.git
cd TheWirelessMonitor

# 2. Run installer
chmod +x install.sh
./install.sh
```

## 📋 What Gets Installed

- **System packages**: python3, python3-pip, python3-venv, git, curl
- **Python packages**: Flask, requests, feedparser, beautifulsoup4, schedule
- **Service**: systemd service for auto-start
- **Database**: SQLite with default RSS feeds
- **Web interface**: Accessible on port 5000

## 🔧 Post-Installation

1. **Access web interface**: http://your-pi-ip:5000
2. **Add RSS feeds**: Use the "RSS Feeds" section
3. **Check admin dashboard**: Monitor system status
4. **Wait for first fetch**: Automatic after 6 hours, or click "Fetch Now"

## 🛠 Management Commands

```bash
# Service management
sudo systemctl status wireless-monitor    # Check status
sudo systemctl restart wireless-monitor   # Restart
sudo systemctl stop wireless-monitor      # Stop
sudo systemctl start wireless-monitor     # Start

# Logs
journalctl -u wireless-monitor -f         # Live logs
journalctl -u wireless-monitor -n 50      # Last 50 lines

# Updates
cd ~/wireless_monitor && git pull         # Update code
sudo systemctl restart wireless-monitor   # Apply updates
```

## 🔍 Verification

After installation, verify everything works:

```bash
# 1. Check service is running
sudo systemctl status wireless-monitor

# 2. Test web interface
curl http://localhost:5000

# 3. Check database
ls -la ~/wireless_monitor/data/

# 4. View logs
journalctl -u wireless-monitor -n 10
```

## 📁 File Locations

- **Installation**: `~/wireless_monitor/`
- **Database**: `~/wireless_monitor/data/wireless_monitor.db`
- **Logs**: `~/wireless_monitor/logs/`
- **Service**: `/etc/systemd/system/wireless-monitor.service`

## 🚨 Troubleshooting

### Installation Fails
```bash
# Check system requirements
python3 --version  # Should be 3.7+
pip3 --version     # Should be available

# Manual dependency install
sudo apt update
sudo apt install python3 python3-pip python3-venv git curl
```

### Service Won't Start
```bash
# Check service logs
journalctl -u wireless-monitor -n 50

# Check file permissions
ls -la ~/wireless_monitor/app/main.py

# Reinstall service
cd ~/wireless_monitor
sudo systemctl stop wireless-monitor
sudo systemctl disable wireless-monitor
sudo rm /etc/systemd/system/wireless-monitor.service
./install.sh
```

### Web Interface Not Accessible
```bash
# Check if service is listening
sudo netstat -tlnp | grep :5000

# Check firewall (if applicable)
sudo ufw status

# Test locally first
curl http://localhost:5000
```

## ⚡ Quick Start

1. **Install**: `curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/install.sh | bash`
2. **Access**: Open http://your-pi-ip:5000 in browser
3. **Configure**: Add RSS feeds in "RSS Feeds" section
4. **Fetch**: Click "Fetch Now" or wait for automatic fetch
5. **Enjoy**: Read wireless technology news!

Total time: **5-10 minutes** from start to finish.