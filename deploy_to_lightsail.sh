#!/bin/bash
# Complete AWS Lightsail Deployment Script for The Signal
# Domain: signal.wirelessnerd.net

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  The Signal - AWS Lightsail Deployment Script             ║${NC}"
echo -e "${BLUE}║  Domain: signal.wirelessnerd.net                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
INSTANCE_NAME="the-signal-prod"
DOMAIN="signal.wirelessnerd.net"
REGION="us-east-1"  # Change if needed
BLUEPRINT_ID="ubuntu_22_04"
BUNDLE_ID="nano_3_0"  # $5/month - 512MB RAM, 1 vCPU, 20GB SSD
KEY_PAIR_NAME="the-signal-key"
STATIC_IP_NAME="the-signal-static-ip"

# Step 1: Check AWS CLI configuration
echo -e "${YELLOW}[1/10] Checking AWS CLI configuration...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not configured!${NC}"
    echo ""
    echo "Please run: aws configure"
    echo "You'll need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region (e.g., us-east-1)"
    echo ""
    exit 1
fi
echo -e "${GREEN}✅ AWS CLI configured${NC}"
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo -e "   Account: ${AWS_ACCOUNT}"
echo ""

# Step 2: Create SSH key pair
echo -e "${YELLOW}[2/10] Creating SSH key pair...${NC}"
if aws lightsail get-key-pair --key-pair-name "$KEY_PAIR_NAME" &> /dev/null; then
    echo -e "${GREEN}✅ Key pair already exists${NC}"
else
    aws lightsail create-key-pair \
        --key-pair-name "$KEY_PAIR_NAME" \
        --query 'privateKeyBase64' \
        --output text > ~/.ssh/${KEY_PAIR_NAME}.pem
    
    chmod 600 ~/.ssh/${KEY_PAIR_NAME}.pem
    echo -e "${GREEN}✅ Key pair created and saved to ~/.ssh/${KEY_PAIR_NAME}.pem${NC}"
fi
echo ""

# Step 3: Create Lightsail instance
echo -e "${YELLOW}[3/10] Creating Lightsail instance...${NC}"
if aws lightsail get-instance --instance-name "$INSTANCE_NAME" &> /dev/null; then
    echo -e "${GREEN}✅ Instance already exists${NC}"
    INSTANCE_STATE=$(aws lightsail get-instance --instance-name "$INSTANCE_NAME" --query 'instance.state.name' --output text)
    echo -e "   State: ${INSTANCE_STATE}"
else
    # Create user data script for initial setup
    USER_DATA=$(cat <<'EOF'
#!/bin/bash
# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y python3 python3-pip git nginx certbot python3-certbot-nginx unzip curl

# Install Caddy (better than nginx for auto-SSL)
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Create app directory
mkdir -p /opt/the-signal
chown ubuntu:ubuntu /opt/the-signal

# Setup complete marker
touch /var/log/lightsail-setup-complete
EOF
)

    aws lightsail create-instances \
        --instance-names "$INSTANCE_NAME" \
        --availability-zone "${REGION}a" \
        --blueprint-id "$BLUEPRINT_ID" \
        --bundle-id "$BUNDLE_ID" \
        --key-pair-name "$KEY_PAIR_NAME" \
        --user-data "$USER_DATA" \
        --tags key=Project,value=TheSignal key=Environment,value=Production
    
    echo -e "${GREEN}✅ Instance created (${BUNDLE_ID} - \$5/month)${NC}"
    echo -e "${YELLOW}   Waiting for instance to be running...${NC}"
    
    # Wait for instance to be running
    while true; do
        STATE=$(aws lightsail get-instance --instance-name "$INSTANCE_NAME" --query 'instance.state.name' --output text)
        if [ "$STATE" == "running" ]; then
            break
        fi
        echo -e "   State: ${STATE}... waiting"
        sleep 5
    done
    echo -e "${GREEN}✅ Instance is running${NC}"
fi
echo ""

# Step 4: Open firewall ports
echo -e "${YELLOW}[4/10] Configuring firewall...${NC}"
aws lightsail put-instance-public-ports \
    --instance-name "$INSTANCE_NAME" \
    --port-infos fromPort=22,toPort=22,protocol=tcp \
                 fromPort=80,toPort=80,protocol=tcp \
                 fromPort=443,toPort=443,protocol=tcp \
                 fromPort=8080,toPort=8080,protocol=tcp &> /dev/null || true
echo -e "${GREEN}✅ Firewall configured (ports 22, 80, 443, 8080)${NC}"
echo ""

# Step 5: Create and attach static IP
echo -e "${YELLOW}[5/10] Creating static IP...${NC}"
if aws lightsail get-static-ip --static-ip-name "$STATIC_IP_NAME" &> /dev/null; then
    echo -e "${GREEN}✅ Static IP already exists${NC}"
else
    aws lightsail allocate-static-ip \
        --static-ip-name "$STATIC_IP_NAME"
    echo -e "${GREEN}✅ Static IP allocated${NC}"
fi

# Attach static IP to instance
aws lightsail attach-static-ip \
    --static-ip-name "$STATIC_IP_NAME" \
    --instance-name "$INSTANCE_NAME" &> /dev/null || true

STATIC_IP=$(aws lightsail get-static-ip --static-ip-name "$STATIC_IP_NAME" --query 'staticIp.ipAddress' --output text)
echo -e "${GREEN}✅ Static IP attached: ${STATIC_IP}${NC}"
echo ""

# Step 6: DNS Configuration Instructions
echo -e "${YELLOW}[6/10] DNS Configuration Required${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Please add this DNS record to wirelessnerd.net:"
echo ""
echo -e "  ${GREEN}Type:${NC}  A"
echo -e "  ${GREEN}Name:${NC}  signal"
echo -e "  ${GREEN}Value:${NC} ${STATIC_IP}"
echo -e "  ${GREEN}TTL:${NC}   300 (or default)"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
read -p "Press Enter after you've added the DNS record..."
echo ""

# Step 7: Wait for instance to be fully ready
echo -e "${YELLOW}[7/10] Waiting for instance to be fully ready...${NC}"
sleep 30  # Give time for user data script to run
echo -e "${GREEN}✅ Instance should be ready${NC}"
echo ""

# Step 8: Get instance connection info
echo -e "${YELLOW}[8/10] Getting connection information...${NC}"
INSTANCE_USER="ubuntu"
echo -e "${GREEN}✅ Connection details:${NC}"
echo -e "   SSH: ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem ${INSTANCE_USER}@${STATIC_IP}"
echo ""

# Step 9: Create deployment package
echo -e "${YELLOW}[9/10] Creating deployment package...${NC}"
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

# Create deployment script for remote server
cat > "$DEPLOY_DIR/remote_setup.sh" << 'REMOTE_EOF'
#!/bin/bash
set -e

echo "🚀 Setting up The Signal on server..."

# Install Python dependencies
cd /opt/the-signal
pip3 install --break-system-packages -r requirements.txt

# Setup Ollama
systemctl start ollama || ollama serve &
sleep 5
ollama pull phi3

# Create systemd service for The Signal
cat > /etc/systemd/system/the-signal.service << 'SERVICE_EOF'
[Unit]
Description=The Signal - Wireless Technology News Aggregator
After=network.target ollama.service

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

# Create systemd service for Ollama
cat > /etc/systemd/system/ollama.service << 'OLLAMA_EOF'
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

# Configure Caddy for auto-SSL
cat > /etc/caddy/Caddyfile << 'CADDY_EOF'
signal.wirelessnerd.net {
    reverse_proxy localhost:8080
    encode gzip
    
    log {
        output file /var/log/caddy/signal.log
    }
}
CADDY_EOF

# Create data directory
mkdir -p /opt/the-signal/data
mkdir -p /opt/the-signal/logs
mkdir -p /opt/the-signal/static/generated_images
chown -R ubuntu:ubuntu /opt/the-signal

# Enable and start services
systemctl daemon-reload
systemctl enable ollama
systemctl enable the-signal
systemctl enable caddy

systemctl restart ollama
sleep 5
systemctl restart the-signal
systemctl restart caddy

echo "✅ Setup complete!"
echo "The Signal is running on port 8080"
echo "Caddy is proxying HTTPS on port 443"
REMOTE_EOF

chmod +x "$DEPLOY_DIR/remote_setup.sh"
echo -e "${GREEN}✅ Deployment package created${NC}"
echo ""

# Step 10: Deploy to server
echo -e "${YELLOW}[10/10] Deploying to server...${NC}"
echo -e "${BLUE}This will:${NC}"
echo -e "  1. Copy files to server"
echo -e "  2. Install dependencies"
echo -e "  3. Setup Ollama AI"
echo -e "  4. Configure systemd services"
echo -e "  5. Setup Caddy with auto-SSL"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Copy files to server
    echo -e "${YELLOW}Copying files to server...${NC}"
    scp -i ~/.ssh/${KEY_PAIR_NAME}.pem -r "$DEPLOY_DIR"/* ${INSTANCE_USER}@${STATIC_IP}:/tmp/the-signal-deploy/
    
    # Run remote setup
    echo -e "${YELLOW}Running setup on server...${NC}"
    ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem ${INSTANCE_USER}@${STATIC_IP} << 'SSH_EOF'
        sudo mv /tmp/the-signal-deploy/* /opt/the-signal/
        sudo bash /opt/the-signal/remote_setup.sh
SSH_EOF
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 DEPLOYMENT COMPLETE!                                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Your application is now live at:${NC}"
    echo -e "  ${GREEN}https://signal.wirelessnerd.net${NC}"
    echo ""
    echo -e "${BLUE}Server Details:${NC}"
    echo -e "  IP Address: ${STATIC_IP}"
    echo -e "  SSH: ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem ubuntu@${STATIC_IP}"
    echo ""
    echo -e "${BLUE}Services:${NC}"
    echo -e "  The Signal: systemctl status the-signal"
    echo -e "  Ollama AI:  systemctl status ollama"
    echo -e "  Caddy:      systemctl status caddy"
    echo ""
    echo -e "${BLUE}Logs:${NC}"
    echo -e "  App:   journalctl -u the-signal -f"
    echo -e "  Caddy: tail -f /var/log/caddy/signal.log"
    echo ""
    echo -e "${BLUE}Cost:${NC} ~\$5/month (Lightsail nano instance)"
    echo ""
else
    echo -e "${YELLOW}Deployment cancelled. Run this script again when ready.${NC}"
fi
