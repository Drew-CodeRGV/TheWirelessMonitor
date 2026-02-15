#!/bin/bash
# Complete the deployment to existing Lightsail instance

set -e

INSTANCE_NAME="the-signal-prod"
STATIC_IP="52.202.235.84"
KEY_PAIR_NAME="the-signal-key"
DOMAIN="signal.wirelessnerd.net"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Complete Deployment to Lightsail                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Instance: $INSTANCE_NAME"
echo "IP: $STATIC_IP"
echo "Domain: $DOMAIN"
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/${KEY_PAIR_NAME}.pem ]; then
    echo "📥 Downloading SSH key..."
    aws lightsail download-default-key-pair \
        --query 'privateKeyBase64' \
        --output text > ~/.ssh/${KEY_PAIR_NAME}.pem
    chmod 600 ~/.ssh/${KEY_PAIR_NAME}.pem
    echo "✅ SSH key saved"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Configuring firewall..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
aws lightsail put-instance-public-ports \
    --instance-name "$INSTANCE_NAME" \
    --port-infos fromPort=22,toPort=22,protocol=tcp \
                 fromPort=80,toPort=80,protocol=tcp \
                 fromPort=443,toPort=443,protocol=tcp \
                 fromPort=8080,toPort=8080,protocol=tcp
echo "✅ Firewall configured"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏳ Waiting for instance to be fully ready (30 seconds)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sleep 30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Creating deployment package..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DEPLOY_DIR="/tmp/the-signal-deploy"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy application files
rsync -av --exclude='.git' \
          --exclude='venv' \
          --exclude='__pycache__' \
          --exclude='*.pyc' \
          --exclude='logs/*.log' \
          --exclude='data/*.db-wal' \
          --exclude='data/*.db-shm' \
          ./ "$DEPLOY_DIR/"

# Create remote setup script
cat > "$DEPLOY_DIR/remote_setup.sh" << 'REMOTE_EOF'
#!/bin/bash
set -e

echo "🚀 Setting up The Signal..."

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip git

# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Setup application
cd /opt/the-signal
pip3 install --break-system-packages -r requirements.txt

# Start Ollama and pull model
sudo systemctl start ollama || (ollama serve &)
sleep 5
ollama pull phi3

# Create systemd services
sudo tee /etc/systemd/system/the-signal.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=The Signal - Wireless Technology News Aggregator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/the-signal
ExecStart=/usr/bin/python3 /opt/the-signal/app/main.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
SERVICE_EOF

sudo tee /etc/systemd/system/ollama.service > /dev/null << 'OLLAMA_EOF'
[Unit]
Description=Ollama AI Service
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
OLLAMA_EOF

# Configure Caddy
sudo tee /etc/caddy/Caddyfile > /dev/null << 'CADDY_EOF'
signal.wirelessnerd.net {
    reverse_proxy localhost:8080
    encode gzip
}
CADDY_EOF

# Create directories
sudo mkdir -p /opt/the-signal/data
sudo mkdir -p /opt/the-signal/logs
sudo mkdir -p /opt/the-signal/static/generated_images
sudo chown -R ubuntu:ubuntu /opt/the-signal

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable ollama the-signal caddy
sudo systemctl restart ollama
sleep 5
sudo systemctl restart the-signal
sudo systemctl restart caddy

echo "✅ Setup complete!"
REMOTE_EOF

chmod +x "$DEPLOY_DIR/remote_setup.sh"
echo "✅ Package created"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Deploying to server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Copy files
echo "📤 Copying files..."
scp -i ~/.ssh/${KEY_PAIR_NAME}.pem \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -r "$DEPLOY_DIR"/* ubuntu@${STATIC_IP}:/tmp/the-signal-deploy/

# Run setup
echo "⚙️  Running setup on server..."
ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    ubuntu@${STATIC_IP} << 'SSH_EOF'
    sudo mkdir -p /opt/the-signal
    sudo mv /tmp/the-signal-deploy/* /opt/the-signal/
    sudo chown -R ubuntu:ubuntu /opt/the-signal
    cd /opt/the-signal
    bash remote_setup.sh
SSH_EOF

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🎉 DEPLOYMENT COMPLETE!                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Your site will be live at: https://signal.wirelessnerd.net"
echo "(After DNS propagates - usually 2-5 minutes)"
echo ""
echo "Server IP: $STATIC_IP"
echo "SSH: ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem ubuntu@${STATIC_IP}"
echo ""
echo "Services:"
echo "  • The Signal: systemctl status the-signal"
echo "  • Ollama AI:  systemctl status ollama"
echo "  • Caddy:      systemctl status caddy"
echo ""
