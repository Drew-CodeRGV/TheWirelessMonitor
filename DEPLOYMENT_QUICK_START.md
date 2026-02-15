# 🚀 Quick Deployment to AWS Lightsail

## One-Command Deployment

```bash
# 1. Setup AWS credentials (first time only)
./setup_aws_credentials.sh

# 2. Deploy everything
./deploy_to_lightsail.sh
```

That's it! The script handles everything automatically.

## What You Need

1. **AWS Account** - Sign up at https://aws.amazon.com
2. **AWS Access Keys** - Get from IAM console
3. **DNS Access** - To add A record for signal.wirelessnerd.net

## During Deployment

The script will pause and show you:
```
Please add this DNS record to wirelessnerd.net:

  Type:  A
  Name:  signal
  Value: 54.123.45.67  (example IP)
  TTL:   300
```

Add this record, then press Enter to continue.

## After Deployment

Your site will be live at:
```
https://signal.wirelessnerd.net
```

SSL certificate is automatic (via Caddy + Let's Encrypt).

## Cost

**$5/month** for Lightsail nano instance
- 512MB RAM
- 1 vCPU
- 20GB SSD
- 1TB data transfer

## Management

### SSH to Server
```bash
ssh -i ~/.ssh/the-signal-key.pem ubuntu@[YOUR_IP]
```

### View Logs
```bash
journalctl -u the-signal -f
```

### Restart App
```bash
sudo systemctl restart the-signal
```

### Update Code
```bash
cd /opt/the-signal
git pull
sudo systemctl restart the-signal
```

## Troubleshooting

**Site not loading?**
```bash
# Check services
systemctl status the-signal
systemctl status caddy

# Check logs
journalctl -u the-signal -n 50
```

**SSL not working?**
- Wait 2-5 minutes for DNS propagation
- Check DNS: `dig signal.wirelessnerd.net`
- Restart Caddy: `sudo systemctl restart caddy`

## Full Documentation

See `AWS_DEPLOYMENT_GUIDE.md` for complete details.
