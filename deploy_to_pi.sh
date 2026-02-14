#!/bin/bash
# Deploy Wireless Monitor to Raspberry Pi

echo "=========================================="
echo "Wireless Monitor - Pi Deployment Script"
echo "=========================================="
echo ""

# Configuration
PI_USER="pi"
PI_HOST=""
PI_PATH="/home/pi/WirelessSignal"

# Get Pi address
read -p "Enter Raspberry Pi address (e.g., 192.168.1.100): " PI_HOST

if [ -z "$PI_HOST" ]; then
    echo "Error: Pi address required"
    exit 1
fi

echo ""
echo "Deployment Steps:"
echo "1. Commit and push code"
echo "2. Transfer credentials"
echo "3. SSH to Pi for setup"
echo ""

# Step 1: Commit code
echo "Step 1: Committing code changes..."
git add .
git status
echo ""
read -p "Commit message: " COMMIT_MSG
git commit -m "$COMMIT_MSG"
git push origin main
echo "✅ Code pushed to GitHub"
echo ""

# Step 2: Transfer credentials
echo "Step 2: Transferring credentials..."
if [ -f "credentials.json" ]; then
    scp credentials.json ${PI_USER}@${PI_HOST}:${PI_PATH}/
    echo "✅ credentials.json transferred"
else
    echo "⚠️  credentials.json not found - you'll need to transfer it manually"
fi

if [ -f "token.json" ]; then
    scp token.json ${PI_USER}@${PI_HOST}:${PI_PATH}/
    echo "✅ token.json transferred"
else
    echo "⚠️  token.json not found - you'll need to transfer it manually"
fi
echo ""

# Step 3: SSH instructions
echo "Step 3: Setting up on Pi..."
echo ""
echo "Now SSH to your Pi and run these commands:"
echo ""
echo "  ssh ${PI_USER}@${PI_HOST}"
echo "  cd ${PI_PATH}"
echo "  git pull origin main"
echo "  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
echo "  chmod 600 credentials.json token.json"
echo "  python3 gmail_api_newsletter_monitor.py  # Test it"
echo ""
echo "To set up as service:"
echo "  sudo cp systemd/*.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable wireless-monitor newsletter-monitor"
echo "  sudo systemctl start wireless-monitor newsletter-monitor"
echo ""
echo "=========================================="
echo "Deployment preparation complete!"
echo "=========================================="
