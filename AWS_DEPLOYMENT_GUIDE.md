# AWS Lightsail Deployment Guide
## The Signal - signal.wirelessnerd.net

## Prerequisites

1. **AWS Account** with billing enabled
2. **Domain access** to wirelessnerd.net DNS settings
3. **AWS Access Keys** (IAM user with Lightsail permissions)

## Quick Start (5 minutes)

### Step 1: Configure AWS CLI

```bash
aws configure
```

You'll need:
- **AWS Access Key ID**: Get from AWS Console → IAM → Users → Security Credentials
- **AWS Secret Access Key**: From same location
- **Default region**: `us-east-1` (or your preferred region)
- **Output format**: `json`

### Step 2: Run Deployment Script

```bash
./deploy_to_lightsail.sh
```

The script will:
1. ✅ Check AWS CLI configuration
2. ✅ Create SSH key pair
3. ✅ Create Lightsail instance ($5/month)
4. ✅ Configure firewall (ports 22, 80, 443, 8080)
5. ✅ Create and attach static IP
6. ⏸️  **PAUSE** - You add DNS record
7. ✅ Deploy application
8. ✅ Setup Ollama AI
9. ✅ Configure Caddy with auto-SSL
10. ✅ Start all services

### Step 3: Add DNS Record

When prompted, add this to your DNS:

```
Type:  A
Name:  signal
Value: [IP shown by script]
TTL:   300
```

**Where to add:**
- If using Route53: AWS Console → Route53 → Hosted Zones → wirelessnerd.net
- If using other DNS: Your domain registrar's DNS management

### Step 4: Wait for SSL

After deployment completes:
- Wait 2-5 minutes for DNS propagation
- Caddy will automatically get SSL certificate from Let's Encrypt
- Visit https://signal.wirelessnerd.net

## What Gets Deployed

### Infrastructure
- **Instance**: Lightsail nano (512MB RAM, 1 vCPU, 20GB SSD)
- **Cost**: $5/month
- **OS**: Ubuntu 22.04 LTS
- **Static IP**: Free (while attached)

### Software Stack
- **Python 3**: Application runtime
- **Flask**: Web framework
- **Ollama + Phi3**: AI for article insights
- **Caddy**: Reverse proxy with auto-SSL
- **SQLite**: Database
- **Systemd**: Service management

### Services Running
1. **the-signal.service**: Main Flask app on port 8080
2. **ollama.service**: AI inference engine
3. **caddy.service**: HTTPS proxy on port 443

## Post-Deployment

### Access Your Site
```
https://signal.wirelessnerd.net
```

### SSH to Server
```bash
ssh -i ~/.ssh/the-signal-key.pem ubuntu@[STATIC_IP]
```

### Check Service Status
```bash
# SSH to server first
systemctl status the-signal
systemctl status ollama
systemctl status caddy
```

### View Logs
```bash
# Application logs
journalctl -u the-signal -f

# Caddy logs
tail -f /var/log/caddy/signal.log

# Ollama logs
journalctl -u ollama -f
```

### Restart Services
```bash
sudo systemctl restart the-signal
sudo systemctl restart ollama
sudo systemctl restart caddy
```

## Updating the Application

### Method 1: Git Pull (Recommended)
```bash
# SSH to server
ssh -i ~/.ssh/the-signal-key.pem ubuntu@[STATIC_IP]

# Pull latest changes
cd /opt/the-signal
git pull origin feature/enhancements

# Restart service
sudo systemctl restart the-signal
```

### Method 2: Re-run Deployment Script
```bash
# On your local machine
./deploy_to_lightsail.sh
```

## Monitoring

### Check Instance Health
```bash
aws lightsail get-instance-state --instance-name the-signal-prod
```

### View Metrics
```bash
# CPU usage
aws lightsail get-instance-metric-data \
  --instance-name the-signal-prod \
  --metric-name CPUUtilization \
  --period 300 \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --unit Percent \
  --statistics Average
```

### Setup Alarms (Optional)
```bash
aws lightsail put-alarm \
  --alarm-name the-signal-high-cpu \
  --monitored-resource-name the-signal-prod \
  --metric-name CPUUtilization \
  --comparison-operator GreaterThanThreshold \
  --threshold 80 \
  --evaluation-periods 2
```

## Scaling Options

### Upgrade Instance Size
```bash
# Create snapshot first
aws lightsail create-instance-snapshot \
  --instance-name the-signal-prod \
  --instance-snapshot-name the-signal-backup-$(date +%Y%m%d)

# Create new instance from snapshot with larger bundle
aws lightsail create-instances-from-snapshot \
  --instance-names the-signal-prod-v2 \
  --instance-snapshot-name the-signal-backup-YYYYMMDD \
  --bundle-id small_3_0  # $10/month - 2GB RAM, 1 vCPU

# Detach static IP from old, attach to new
aws lightsail detach-static-ip --static-ip-name the-signal-static-ip
aws lightsail attach-static-ip \
  --static-ip-name the-signal-static-ip \
  --instance-name the-signal-prod-v2
```

### Available Bundles
- `nano_3_0`: $5/month - 512MB RAM, 1 vCPU, 20GB SSD
- `micro_3_0`: $7/month - 1GB RAM, 1 vCPU, 40GB SSD
- `small_3_0`: $10/month - 2GB RAM, 1 vCPU, 60GB SSD
- `medium_3_0`: $20/month - 4GB RAM, 2 vCPU, 80GB SSD

## Backup Strategy

### Automatic Snapshots
```bash
# Enable automatic snapshots (daily at 2 AM UTC)
aws lightsail enable-add-on \
  --resource-name the-signal-prod \
  --add-on-request addOnType=AutoSnapshot
```

### Manual Snapshot
```bash
aws lightsail create-instance-snapshot \
  --instance-name the-signal-prod \
  --instance-snapshot-name the-signal-manual-$(date +%Y%m%d-%H%M)
```

### Database Backup
```bash
# SSH to server and backup database
ssh -i ~/.ssh/the-signal-key.pem ubuntu@[STATIC_IP]
cd /opt/the-signal
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# Download to local machine
scp -i ~/.ssh/the-signal-key.pem ubuntu@[STATIC_IP]:/opt/the-signal/backup-*.tar.gz ./
```

## Troubleshooting

### Site Not Loading
```bash
# Check if services are running
ssh -i ~/.ssh/the-signal-key.pem ubuntu@[STATIC_IP]
systemctl status the-signal
systemctl status caddy

# Check logs
journalctl -u the-signal -n 50
journalctl -u caddy -n 50
```

### SSL Certificate Issues
```bash
# Check Caddy logs
tail -f /var/log/caddy/signal.log

# Restart Caddy
sudo systemctl restart caddy

# Verify DNS is pointing to correct IP
dig signal.wirelessnerd.net
```

### AI Not Working
```bash
# Check Ollama service
systemctl status ollama

# Test Ollama
ollama list
ollama run phi3 "test"

# Restart Ollama
sudo systemctl restart ollama
```

### Out of Disk Space
```bash
# Check disk usage
df -h

# Clean up old logs
sudo journalctl --vacuum-time=7d

# Clean up old snapshots in AWS Console
```

## Cost Breakdown

### Monthly Costs
- Lightsail instance (nano): $5.00
- Static IP: $0.00 (free while attached)
- Data transfer: First 1TB free
- **Total: ~$5/month**

### Additional Costs (if needed)
- Snapshots: $0.05/GB/month
- Load balancer: $18/month (if you add later)
- Extra data transfer: $0.09/GB (after 1TB)

## Security Best Practices

### 1. Update SSH Key Permissions
```bash
chmod 600 ~/.ssh/the-signal-key.pem
```

### 2. Setup Firewall Rules
Already configured by script:
- Port 22: SSH (your IP only recommended)
- Port 80: HTTP (redirects to HTTPS)
- Port 443: HTTPS
- Port 8080: Blocked externally (only localhost)

### 3. Regular Updates
```bash
# SSH to server
ssh -i ~/.ssh/the-signal-key.pem ubuntu@[STATIC_IP]

# Update system
sudo apt update && sudo apt upgrade -y

# Restart if kernel updated
sudo reboot
```

### 4. Monitor Access Logs
```bash
# SSH attempts
sudo tail -f /var/log/auth.log

# Web access
tail -f /var/log/caddy/signal.log
```

## Cleanup / Deletion

### Delete Everything
```bash
# Detach and release static IP
aws lightsail detach-static-ip --static-ip-name the-signal-static-ip
aws lightsail release-static-ip --static-ip-name the-signal-static-ip

# Delete instance
aws lightsail delete-instance --instance-name the-signal-prod

# Delete key pair
aws lightsail delete-key-pair --key-pair-name the-signal-key
rm ~/.ssh/the-signal-key.pem

# Delete snapshots (if any)
aws lightsail get-instance-snapshots --query 'instanceSnapshots[*].name' --output text | \
  xargs -I {} aws lightsail delete-instance-snapshot --instance-snapshot-name {}
```

## Support

### AWS Lightsail Documentation
https://docs.aws.amazon.com/lightsail/

### Caddy Documentation
https://caddyserver.com/docs/

### Ollama Documentation
https://ollama.ai/docs/

### The Signal Repository
https://github.com/Drew-CodeRGV/TheWirelessMonitor

## Next Steps

After deployment:
1. ✅ Test the site: https://signal.wirelessnerd.net
2. ✅ Check admin panel: https://signal.wirelessnerd.net/admin
3. ✅ Verify AI insights: https://signal.wirelessnerd.net/insights
4. ✅ Setup monitoring/alerts
5. ✅ Configure automatic backups
6. ✅ Add to your monitoring dashboard

Enjoy your new deployment! 🚀
