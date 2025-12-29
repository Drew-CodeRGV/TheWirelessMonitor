# The Wireless Monitor

An automated RSS news aggregation system that fetches RSS feeds, analyzes stories using AI, and provides a web interface for viewing top stories in the Wi-Fi/wireless industry with classic 1990s newspaper styling.

## Features

- **Web Interface**: Clean, responsive dashboard for viewing and managing content
- **RSS Feed Management**: Add individual feeds or bulk import multiple feeds
- **AI-Powered Analysis**: Local LLM analyzes stories for Wi-Fi/wireless relevance
- **Entertainment Detection**: AI identifies fun, viral, and entertaining tech stories  
- **Daily Automated Fetching**: RSS feeds fetched every 6 hours automatically
- **Weekly Digest**: Comprehensive weekly summary of top stories
- **Podcast Script Generation**: AI creates scripts in Drew Lentz's voice for Waves Wireless Podcast
- **Auto-Update System**: Checks GitHub every 8 hours and updates automatically
- **Admin Console**: System management, update control, and monitoring
- **Health Monitoring**: Automatic service monitoring and restart capabilities
- **Fully Automated Startup**: Starts on boot, zero maintenance required

## System Architecture

- **Backend**: Python Flask application with SQLite database
- **AI Analysis**: Local LLM using Ollama (Llama2) for content analysis
- **Auto-Updates**: GitHub integration with automated version checking
- **Scheduler**: Cron jobs for RSS fetching, updates, and monitoring
- **Web Interface**: Bootstrap-based responsive UI with admin console
- **Entertainment Detection**: AI identifies viral, funny, and creative wireless stories
- **Podcast Integration**: Generates scripts mimicking Drew Lentz's speaking style
- **Health Monitoring**: Automatic service monitoring and recovery
- **Auto-start**: systemd service with nginx reverse proxy

## Installation Options

### Smart Installation (Recommended for Development)
The smart installer detects existing installations and gives you options:

```bash
# Smart installer with detection and options
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/smart_install.sh | bash
```

**Installation Types:**
- **Clean Install**: Remove everything, start fresh (with optional data backup)
- **Upgrade Install**: Keep data, update code and configuration  
- **Quick Fix**: Fix common issues without reinstalling
- **Fresh Install**: First-time installation

### Development Reset (Fast Iteration)
For development and testing - keeps system packages, resets application:

```bash
# Quick reset for development
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/dev_reset.sh | bash
```

**Options:**
- Keep or reset database
- Preserve working Python environment
- Update code from repository
- Restart services

### Status Checker
Check what's installed and working:

```bash
# Check system status
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/check_status.sh | bash
```

### Traditional Installation Methods

**Standard Installation:**
```bash
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/scripts/install.sh | bash
```

**Universal Installation (any user/OS):**
```bash
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/universal_install.sh | bash
```

**WiFi User Specific:**
```bash
curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/install_wifi_user.sh | bash
```

This will:
- Install all system dependencies
- Set up Python environment
- Install and configure Ollama AI
- Create systemd services for auto-start
- Configure nginx reverse proxy
- Set up automated cron jobs
- Initialize the database with default RSS feeds

## Why Use Smart Installation?

### 🚀 **Development Friendly**
- **No more wiping your Pi**: Keep system packages between installs
- **Fast iteration**: Reset just the app, not the entire system
- **Data preservation**: Choose to keep or reset your database
- **Intelligent detection**: Knows what's already installed

### 🛠 **Installation Types**
- **Clean Install**: Fresh start with optional data backup
- **Upgrade Install**: Update code while preserving data
- **Quick Fix**: Repair common issues without full reinstall
- **Status Check**: See exactly what's installed and working

### ⚡ **Time Savings**
- **System packages**: Skip reinstalling Python, nginx, ollama if already present
- **Python environment**: Reuse working virtual environments
- **Configuration**: Smart service and config management
- **Testing**: Quick reset between development iterations

### 🔧 **Smart Features**
- **Automatic backup**: Preserves data during upgrades
- **Service management**: Proper cleanup and restart of services
- **Error recovery**: Fix common path and import issues
- **Status monitoring**: Know exactly what's working

## Manual Installation

If you prefer to install manually or customize the setup:

1. Clone the repository:
```bash
git clone https://github.com/Drew-CodeRGV/TheWirelessMonitor.git
cd TheWirelessMonitor
```

2. Run the installation script:
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

## Post-Installation

After installation, the system will be accessible at:
- **Web Interface**: `http://your-pi-ip-address`
- **Default Port**: 80 (via nginx proxy)

The system automatically:
- Fetches RSS feeds every 6 hours
- Generates weekly digests on Monday mornings
- Starts on boot via systemd

## Directory Structure

```
├── app/
│   ├── main.py              # Flask application with admin console
│   ├── models.py            # Database models with new tables
│   ├── rss_fetcher.py       # RSS feed processing
│   ├── ai_analyzer.py       # AI analysis + entertainment detection + podcast scripts
│   ├── updater.py           # Auto-update system
│   ├── github_manager.py    # GitHub integration
│   └── templates/           # HTML templates including admin console
├── static/                  # CSS, JS, images
├── config/
│   ├── feeds.json          # Default RSS feeds
│   └── settings.py         # Enhanced configuration
├── scripts/
│   ├── install.sh          # Main installation script
│   ├── auto_update.py      # Automated update checker
│   ├── monitor.sh          # System health monitoring
│   └── daily_fetch.py      # Cron job script
├── version.json            # Version tracking
└── requirements.txt        # Python dependencies
```

## Configuration

### Adding RSS Feeds

1. Access the web interface at `http://your-pi-ip`
2. Navigate to "Manage Feeds"
3. Add RSS URLs for Wi-Fi/wireless industry sources
4. Toggle feeds active/inactive as needed

### Default Feeds Included

- Ars Technica
- TechCrunch  
- The Verge
- IEEE Spectrum
- Wi-Fi Alliance News
- Wireless Week
- RCR Wireless
- Light Reading
- Fierce Wireless
- Mobile World Live

## New Features Added

### Auto-Update System
- Checks GitHub every 8 hours for new versions
- Automatically downloads and installs updates
- Admin console shows current version and update status
- Manual update control through web interface

### Admin Console
- System status monitoring and health checks
- Update management (check/install updates)
- Quick actions (fetch RSS, generate podcast, restart services)
- System statistics and update history

### Bulk RSS Feed Management  
- Add multiple RSS feeds at once via textarea
- Suggested feeds for Wi-Fi/wireless industry
- One-click addition of recommended sources
- Support for Name|URL format or just URLs

### Entertainment Story Detection
- AI identifies fun, viral, and entertaining wireless stories
- Separate entertainment score (0-100%) for each article
- Dedicated "Fun Stories" section in web interface
- Detects creative hacks, epic fails, viral content, and record breakers

### Podcast Script Generation
- AI generates scripts in Drew Lentz's voice and style
- Based on analysis of his speaking patterns and expertise
- Uses weekly top stories as source material
- Mimics his conversational, practical approach
- Includes his catchphrases and technical focus areas

### GitHub Integration
- **Repository Publishing**: One-click publishing to GitHub
- **Version Control**: Automatic commit and version tracking  
- **Collaboration**: Share your customized news aggregator
- **Backup**: Keep your project safely stored in the cloud
- **Open Source**: Contribute to the wireless community
- Health check script runs every 15 minutes
- Automatic service restart if failures detected
- System status API for real-time monitoring
- Comprehensive logging and error tracking

### Customization

Edit `/home/wifi/rss_aggregator/config/settings.py` to:
- Modify Wi-Fi keywords for better relevance detection
- Adjust fetch intervals
- Configure email notifications
- Change AI model settings

## Management Commands

```bash
# Check system status
sudo systemctl status rss-aggregator

# View logs
journalctl -u rss-aggregator -f
tail -f /home/wifi/rss_aggregator/logs/cron.log

# Manual operations
cd /home/wifi/rss_aggregator
source venv/bin/activate
python scripts/daily_fetch.py      # Manual RSS fetch
python scripts/weekly_digest.py    # Generate weekly digest

# Update system
./update.sh
```

## Troubleshooting

### Common Issues

1. **Ollama not responding**: 
   ```bash
   sudo systemctl restart ollama
   ollama pull llama2:7b-chat
   ```

2. **Web interface not accessible**:
   ```bash
   sudo systemctl status nginx
   sudo systemctl status rss-aggregator
   ```

3. **Database issues**:
   ```bash
   cd /home/wifi/rss_aggregator
   python3 -c "from app.models import init_db; init_db()"
   ```

4. **Cron jobs not running**:
   ```bash
   crontab -l  # Check cron jobs
   sudo systemctl status cron
   ```

### Performance Optimization

For better performance on Raspberry Pi:
- Use Raspberry Pi 4 with 4GB+ RAM
- Use fast SD card (Class 10 or better)
- Consider USB 3.0 SSD for database storage
- Limit concurrent RSS fetches in settings

## Security Considerations

- Change default secret key in production
- Consider setting up HTTPS with Let's Encrypt
- Regularly update system packages
- Monitor log files for unusual activity
- Restrict network access if needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on Raspberry Pi
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the troubleshooting section
- Review system logs
- Open an issue on GitHub
- Ensure your Raspberry Pi meets minimum requirements

---

**Minimum Requirements:**
- Raspberry Pi 3B+ or newer
- 2GB RAM (4GB recommended)
- 16GB SD card (32GB recommended)
- Internet connection
- Fresh Raspberry Pi OS installation