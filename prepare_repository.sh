#!/bin/bash

# Script to prepare The Wireless Monitor files for GitHub repository
# This copies only the necessary files, excluding Kiro-specific files

set -e

echo "🚀 Preparing The Wireless Monitor repository files..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create target directory
TARGET_DIR="$HOME/TheWirelessMonitor"
CURRENT_DIR=$(pwd)

print_status "Creating repository directory: $TARGET_DIR"
mkdir -p "$TARGET_DIR"

# Create directory structure
print_status "Creating directory structure..."
mkdir -p "$TARGET_DIR/app/templates"
mkdir -p "$TARGET_DIR/static"
mkdir -p "$TARGET_DIR/config"
mkdir -p "$TARGET_DIR/scripts"

# Copy root files
print_status "Copying root files..."
cp "$CURRENT_DIR/README.md" "$TARGET_DIR/" 2>/dev/null || print_warning "README.md not found"
cp "$CURRENT_DIR/requirements.txt" "$TARGET_DIR/" 2>/dev/null || print_warning "requirements.txt not found"
cp "$CURRENT_DIR/version.json" "$TARGET_DIR/" 2>/dev/null || print_warning "version.json not found"
cp "$CURRENT_DIR/DEPLOYMENT.md" "$TARGET_DIR/" 2>/dev/null || print_warning "DEPLOYMENT.md not found"
cp "$CURRENT_DIR/universal_install.sh" "$TARGET_DIR/" 2>/dev/null || print_warning "universal_install.sh not found"
cp "$CURRENT_DIR/bootstrap_install.sh" "$TARGET_DIR/" 2>/dev/null || print_warning "bootstrap_install.sh not found"
cp "$CURRENT_DIR/github_upload_checklist.md" "$TARGET_DIR/" 2>/dev/null || print_warning "github_upload_checklist.md not found"
cp "$CURRENT_DIR/WIRELESS_MONITOR_FILES.md" "$TARGET_DIR/" 2>/dev/null || print_warning "WIRELESS_MONITOR_FILES.md not found"

# Copy app files
print_status "Copying app files..."
cp "$CURRENT_DIR/app/main.py" "$TARGET_DIR/app/" 2>/dev/null || print_warning "app/main.py not found"
cp "$CURRENT_DIR/app/models.py" "$TARGET_DIR/app/" 2>/dev/null || print_warning "app/models.py not found"
cp "$CURRENT_DIR/app/rss_fetcher.py" "$TARGET_DIR/app/" 2>/dev/null || print_warning "app/rss_fetcher.py not found"
cp "$CURRENT_DIR/app/ai_analyzer.py" "$TARGET_DIR/app/" 2>/dev/null || print_warning "app/ai_analyzer.py not found"
cp "$CURRENT_DIR/app/updater.py" "$TARGET_DIR/app/" 2>/dev/null || print_warning "app/updater.py not found"
cp "$CURRENT_DIR/app/github_manager.py" "$TARGET_DIR/app/" 2>/dev/null || print_warning "app/github_manager.py not found"

# Copy templates
print_status "Copying templates..."
cp "$CURRENT_DIR/app/templates/base.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "base.html not found"
cp "$CURRENT_DIR/app/templates/index.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "index.html not found"
cp "$CURRENT_DIR/app/templates/article.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "article.html not found"
cp "$CURRENT_DIR/app/templates/admin.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "admin.html not found"
cp "$CURRENT_DIR/app/templates/entertainment.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "entertainment.html not found"
cp "$CURRENT_DIR/app/templates/social_config.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "social_config.html not found"
cp "$CURRENT_DIR/app/templates/github_config.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "github_config.html not found"
cp "$CURRENT_DIR/app/templates/feeds.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "feeds.html not found"
cp "$CURRENT_DIR/app/templates/weekly.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "weekly.html not found"
cp "$CURRENT_DIR/app/templates/podcast.html" "$TARGET_DIR/app/templates/" 2>/dev/null || print_warning "podcast.html not found"

# Copy static files
print_status "Copying static files..."
cp "$CURRENT_DIR/static/style.css" "$TARGET_DIR/static/" 2>/dev/null || print_warning "style.css not found"
cp "$CURRENT_DIR/static/app.js" "$TARGET_DIR/static/" 2>/dev/null || print_warning "app.js not found"
cp "$CURRENT_DIR/static/default-share-image.png" "$TARGET_DIR/static/" 2>/dev/null || print_warning "default-share-image.png not found"

# Copy config files
print_status "Copying config files..."
cp "$CURRENT_DIR/config/settings.py" "$TARGET_DIR/config/" 2>/dev/null || print_warning "settings.py not found"

# Copy scripts
print_status "Copying scripts..."
cp "$CURRENT_DIR/scripts/install.sh" "$TARGET_DIR/scripts/" 2>/dev/null || print_warning "install.sh not found"
cp "$CURRENT_DIR/scripts/auto_update.py" "$TARGET_DIR/scripts/" 2>/dev/null || print_warning "auto_update.py not found"
cp "$CURRENT_DIR/scripts/monitor.sh" "$TARGET_DIR/scripts/" 2>/dev/null || print_warning "monitor.sh not found"

# Make scripts executable
print_status "Making scripts executable..."
chmod +x "$TARGET_DIR/universal_install.sh" 2>/dev/null || true
chmod +x "$TARGET_DIR/bootstrap_install.sh" 2>/dev/null || true
chmod +x "$TARGET_DIR/scripts/install.sh" 2>/dev/null || true
chmod +x "$TARGET_DIR/scripts/monitor.sh" 2>/dev/null || true

# Create .gitignore for the repository
print_status "Creating .gitignore..."
cat > "$TARGET_DIR/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Local configuration
config/local_settings.py
.env

# Data directories
data/
backups/

# Temporary files
tmp/
temp/
EOF

# Initialize git repository
print_status "Initializing git repository..."
cd "$TARGET_DIR"
git init
git add .
git commit -m "Initial commit: The Wireless Monitor RSS Aggregator

Features:
- RSS feed aggregation with AI analysis
- Classic 1990s newspaper layout
- Social media sharing integration
- GitHub publishing capabilities
- Automated updates and monitoring
- Entertainment story detection
- Podcast script generation in Drew Lentz's voice"

print_success "Repository prepared successfully!"
echo ""
echo "📁 Repository location: $TARGET_DIR"
echo ""
echo "🚀 Next steps:"
echo "1. Create repository on GitHub: https://github.com/new"
echo "   - Repository name: TheWirelessMonitor"
echo "   - Make it public"
echo ""
echo "2. Push to GitHub:"
echo "   cd $TARGET_DIR"
echo "   git remote add origin https://github.com/Drew-CodeRGV/TheWirelessMonitor.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Test installation:"
echo "   curl -sSL https://raw.githubusercontent.com/Drew-CodeRGV/TheWirelessMonitor/main/universal_install.sh | bash"
echo ""
print_warning "Make sure to create the GitHub repository before pushing!"