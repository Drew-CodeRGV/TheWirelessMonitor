#!/bin/bash

# Smart Installation Script for The Wireless Monitor
# Detects existing installations and provides clean/upgrade options

set -e

echo "🚀 Smart Installation for The Wireless Monitor"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Configuration
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/rss_aggregator"
REPO_URL="https://github.com/Drew-CodeRGV/TheWirelessMonitor.git"
SERVICE_NAME="rss-aggregator"
BACKUP_DIR="$USER_HOME/rss_backup_$(date +%Y%m%d_%H%M%S)"

# Detection functions
check_existing_installation() {
    local has_install=false
    local has_service=false
    local has_database=false
    local has_venv=false
    
    if [ -d "$INSTALL_DIR" ]; then
        has_install=true
        print_status "Found existing installation at: $INSTALL_DIR"
    fi
    
    if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME.service"; then
        has_service=true
        print_status "Found existing systemd service: $SERVICE_NAME"
    fi
    
    if [ -f "$INSTALL_DIR/data/news.db" ]; then
        has_database=true
        print_status "Found existing database with data"
    fi
    
    if [ -d "$INSTALL_DIR/venv" ]; then
        has_venv=true
        print_status "Found existing Python virtual environment"
    fi
    
    echo "$has_install,$has_service,$has_database,$has_venv"
}

check_system_packages() {
    local packages_installed=true
    
    # Check key packages
    if ! command -v python3 &> /dev/null; then packages_installed=false; fi
    if ! command -v git &> /dev/null; then packages_installed=false; fi
    if ! command -v nginx &> /dev/null; then packages_installed=false; fi
    if ! command -v ollama &> /dev/null; then packages_installed=false; fi
    
    if [ "$packages_installed" = true ]; then
        print_success "System packages already installed"
        return 0
    else
        print_warning "Some system packages missing"
        return 1
    fi
}

backup_existing_data() {
    print_header "Creating backup of existing data..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [ -f "$INSTALL_DIR/data/news.db" ]; then
        cp "$INSTALL_DIR/data/news.db" "$BACKUP_DIR/"
        print_status "Database backed up"
    fi
    
    # Backup configuration
    if [ -f "$INSTALL_DIR/config/settings.py" ]; then
        cp "$INSTALL_DIR/config/settings.py" "$BACKUP_DIR/"
        print_status "Configuration backed up"
    fi
    
    # Backup logs
    if [ -d "$INSTALL_DIR/logs" ]; then
        cp -r "$INSTALL_DIR/logs" "$BACKUP_DIR/"
        print_status "Logs backed up"
    fi
    
    # Backup cron jobs
    crontab -l > "$BACKUP_DIR/crontab_backup.txt" 2>/dev/null || true
    
    print_success "Backup created at: $BACKUP_DIR"
}

restore_data() {
    if [ -d "$BACKUP_DIR" ]; then
        print_header "Restoring backed up data..."
        
        # Restore database
        if [ -f "$BACKUP_DIR/news.db" ]; then
            mkdir -p "$INSTALL_DIR/data"
            cp "$BACKUP_DIR/news.db" "$INSTALL_DIR/data/"
            print_status "Database restored"
        fi
        
        # Restore logs
        if [ -d "$BACKUP_DIR/logs" ]; then
            cp -r "$BACKUP_DIR/logs" "$INSTALL_DIR/"
            print_status "Logs restored"
        fi
        
        print_success "Data restoration completed"
    fi
}

clean_existing_installation() {
    print_header "Cleaning existing installation..."
    
    # Stop services
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        print_status "Stopping $SERVICE_NAME service..."
        sudo systemctl stop "$SERVICE_NAME"
    fi
    
    # Remove systemd service
    if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
        print_status "Removing systemd service..."
        sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true
        sudo rm -f "/etc/systemd/system/$SERVICE_NAME.service"
        sudo systemctl daemon-reload
    fi
    
    # Clean cron jobs
    print_status "Cleaning cron jobs..."
    crontab -l 2>/dev/null | grep -v "rss_aggregator\|RSS Aggregator" | crontab - || true
    
    # Remove nginx config
    if [ -f "/etc/nginx/sites-enabled/rss-aggregator" ]; then
        print_status "Removing nginx configuration..."
        sudo rm -f /etc/nginx/sites-enabled/rss-aggregator
        sudo rm -f /etc/nginx/sites-available/rss-aggregator
        sudo systemctl reload nginx 2>/dev/null || true
    fi
    
    # Remove installation directory (but preserve backup)
    if [ -d "$INSTALL_DIR" ] && [ "$INSTALL_DIR" != "$USER_HOME" ]; then
        print_status "Removing installation directory..."
        rm -rf "$INSTALL_DIR"
    fi
    
    print_success "Existing installation cleaned"
}

install_system_packages() {
    print_header "Installing/updating system packages..."
    
    # Update package list
    sudo apt update
    
    # Install system dependencies
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        wget \
        sqlite3 \
        nginx \
        supervisor \
        cron \
        build-essential \
        python3-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        libjpeg62-turbo-dev \
        libfreetype6-dev \
        libtiff5-dev \
        libopenjp2-7-dev \
        libwebp-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libxcb1-dev \
        zlib1g-dev \
        libffi-dev \
        libssl-dev \
        pkg-config \
        gfortran \
        libopenblas-dev \
        liblapack-dev \
        python3-numpy \
        python3-scipy
    
    # Install Ollama if not present
    if ! command -v ollama &> /dev/null; then
        print_status "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        sudo systemctl enable ollama
        sudo systemctl start ollama
        sleep 5
        ollama pull llama2:7b-chat
    else
        print_status "Ollama already installed"
        # Ensure it's running
        sudo systemctl start ollama || true
    fi
    
    print_success "System packages ready"
}

install_application() {
    print_header "Installing The Wireless Monitor application..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Clone or update repository
    if [ -d ".git" ]; then
        print_status "Updating from repository..."
        git pull origin main
    else
        print_status "Cloning repository..."
        git clone "$REPO_URL" .
    fi
    
    # Create Python virtual environment
    print_status "Setting up Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Increase swap for compilation if on Raspberry Pi
    if [ -f /proc/device-tree/model ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
        print_status "Temporarily increasing swap space..."
        sudo dphys-swapfile swapoff || true
        sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile || true
        sudo dphys-swapfile setup || true
        sudo dphys-swapfile swapon || true
    fi
    
    # Install Python packages
    pip install --upgrade pip setuptools wheel
    pip install --upgrade Pillow
    
    if ! pip install -r requirements.txt; then
        print_warning "Full requirements failed, using lightweight version..."
        pip install -r requirements-lite.txt
    fi
    
    # Restore swap size
    if [ -f /proc/device-tree/model ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
        print_status "Restoring swap size..."
        sudo dphys-swapfile swapoff || true
        sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=100/' /etc/dphys-swapfile || true
        sudo dphys-swapfile setup || true
        sudo dphys-swapfile swapon || true
    fi
    
    # Download NLTK data
    python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" || true
    
    # Create directories
    mkdir -p data logs
    
    # Initialize database (only if no backup to restore)
    if [ ! -f "$BACKUP_DIR/news.db" ]; then
        print_status "Initializing fresh database..."
        python3 -c "from app.models import init_db; init_db()"
    fi
    
    print_success "Application installed"
}

setup_services() {
    print_header "Setting up system services..."
    
    # Create systemd service
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=The Wireless Monitor RSS Aggregator
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app.main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Configure nginx
    sudo tee /etc/nginx/sites-available/rss-aggregator > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $INSTALL_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable services
    sudo ln -sf /etc/nginx/sites-available/rss-aggregator /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl reload nginx
    
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    sudo systemctl start $SERVICE_NAME
    
    # Setup cron jobs
    (crontab -l 2>/dev/null; echo "# The Wireless Monitor automated tasks") | crontab -
    (crontab -l 2>/dev/null; echo "0 */6 * * * cd $INSTALL_DIR && PYTHONPATH=$INSTALL_DIR ./venv/bin/python scripts/daily_fetch.py >> logs/cron.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 8 * * 1 cd $INSTALL_DIR && PYTHONPATH=$INSTALL_DIR ./venv/bin/python scripts/weekly_digest.py >> logs/cron.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "0 */8 * * * cd $INSTALL_DIR && PYTHONPATH=$INSTALL_DIR ./venv/bin/python scripts/auto_update.py >> logs/update.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "*/15 * * * * $INSTALL_DIR/scripts/monitor.sh >> logs/monitor.log 2>&1") | crontab -
    
    print_success "Services configured and started"
}

# Main installation logic
main() {
    echo ""
    echo "======================================"
    echo "  The Wireless Monitor Smart Install  "
    echo "======================================"
    echo ""
    
    print_status "Detecting existing installation..."
    
    # Check what's already installed
    IFS=',' read -r has_install has_service has_database has_venv <<< "$(check_existing_installation)"
    
    if [ "$has_install" = "true" ]; then
        echo ""
        print_warning "Existing installation detected!"
        echo ""
        echo "Choose installation type:"
        echo "1) Clean Install - Remove everything and start fresh"
        echo "2) Upgrade Install - Keep data, update code and config"
        echo "3) Quick Fix - Just fix common issues, keep everything"
        echo "4) Cancel installation"
        echo ""
        read -p "Enter your choice (1-4): " choice
        
        case $choice in
            1)
                print_header "Starting Clean Installation..."
                if [ "$has_database" = "true" ]; then
                    read -p "Backup existing data before clean install? (y/N): " backup_choice
                    if [[ $backup_choice =~ ^[Yy]$ ]]; then
                        backup_existing_data
                    fi
                fi
                clean_existing_installation
                ;;
            2)
                print_header "Starting Upgrade Installation..."
                backup_existing_data
                clean_existing_installation
                ;;
            3)
                print_header "Starting Quick Fix..."
                cd "$INSTALL_DIR"
                source venv/bin/activate
                PYTHONPATH="$INSTALL_DIR" python3 scripts/daily_fetch.py || true
                sudo systemctl restart $SERVICE_NAME || true
                print_success "Quick fix completed!"
                exit 0
                ;;
            4)
                print_status "Installation cancelled"
                exit 0
                ;;
            *)
                print_error "Invalid choice"
                exit 1
                ;;
        esac
    else
        print_header "Starting Fresh Installation..."
    fi
    
    # Check if system packages are installed
    if ! check_system_packages; then
        install_system_packages
    else
        print_status "Skipping system package installation (already installed)"
    fi
    
    # Install application
    install_application
    
    # Restore data if we have a backup
    if [ "$choice" = "2" ] || [[ $backup_choice =~ ^[Yy]$ ]]; then
        restore_data
    fi
    
    # Setup services
    setup_services
    
    # Test the installation
    print_header "Testing installation..."
    cd "$INSTALL_DIR"
    source venv/bin/activate
    if PYTHONPATH="$INSTALL_DIR" python3 scripts/daily_fetch.py; then
        print_success "✅ Installation test passed!"
    else
        print_warning "Installation test had issues, but services are running"
    fi
    
    # Display completion info
    echo ""
    print_success "🎉 The Wireless Monitor installation completed!"
    echo ""
    echo "📋 System Information:"
    echo "   • Installation: $INSTALL_DIR"
    echo "   • Web interface: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost')"
    echo "   • Service status: sudo systemctl status $SERVICE_NAME"
    echo "   • Logs: journalctl -u $SERVICE_NAME -f"
    if [ -d "$BACKUP_DIR" ]; then
        echo "   • Backup location: $BACKUP_DIR"
    fi
    echo ""
    echo "🔧 Quick Commands:"
    echo "   • Restart: sudo systemctl restart $SERVICE_NAME"
    echo "   • Update: cd $INSTALL_DIR && git pull && sudo systemctl restart $SERVICE_NAME"
    echo "   • Manual fetch: cd $INSTALL_DIR && source venv/bin/activate && PYTHONPATH=$INSTALL_DIR python3 scripts/daily_fetch.py"
    echo ""
    print_warning "Visit the web interface to configure your RSS feeds!"
}

# Run main function
main "$@"