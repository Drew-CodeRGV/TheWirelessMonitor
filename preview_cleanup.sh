#!/bin/bash

# Preview Repository Cleanup - Shows what will be removed/changed

echo "🔍 Repository Cleanup Preview"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_remove() { echo -e "${RED}[-]${NC} $1"; }
print_keep() { echo -e "${GREEN}[+]${NC} $1"; }
print_rename() { echo -e "${YELLOW}[→]${NC} $1"; }
print_create() { echo -e "${BLUE}[*]${NC} $1"; }

echo "Files that will be REMOVED:"
echo "──────────────────────────────"
print_remove "app/main.py (old complex version)"
print_remove "app/models.py"
print_remove "app/rss_fetcher.py"
print_remove "app/ai_analyzer.py"
print_remove "app/updater.py"
print_remove "app/github_manager.py"
print_remove "app/templates/base.html (old version)"
print_remove "app/templates/index.html (old version)"
print_remove "app/templates/article.html"
print_remove "app/templates/admin.html (old version)"
print_remove "app/templates/entertainment.html"
print_remove "app/templates/feeds.html (old version)"
print_remove "app/templates/weekly.html"
print_remove "app/templates/podcast.html"
print_remove "app/templates/github_config.html"
print_remove "app/templates/social_config.html"
print_remove "config/ (entire directory)"
print_remove "scripts/ (entire directory)"
print_remove "static/ (entire directory)"
print_remove "All old installation scripts (8 files)"
print_remove "All troubleshooting scripts (8 files)"
print_remove "requirements.txt (old heavy version)"
print_remove "requirements-lite.txt"
print_remove "DEPLOYMENT.md (old complex docs)"

echo ""
echo "Files that will be RENAMED:"
echo "──────────────────────────────"
print_rename "app/simple_main.py → app/main.py"
print_rename "app/templates/simple_base.html → app/templates/base.html"
print_rename "app/templates/simple_index.html → app/templates/index.html"
print_rename "app/templates/simple_feeds.html → app/templates/feeds.html"
print_rename "app/templates/simple_admin.html → app/templates/admin.html"
print_rename "requirements-minimal.txt → requirements.txt"
print_rename "simple_install.sh → install.sh"

echo ""
echo "Files that will be CREATED:"
echo "──────────────────────────────"
print_create "README.md (new streamlined version)"
print_create "INSTALLATION.md (simple installation guide)"
print_create "version.json (streamlined edition info)"

echo ""
echo "Files that will be KEPT:"
echo "──────────────────────────────"
print_keep "STREAMLINED_COMPARISON.md"
print_keep "cleanup_repository.sh"
print_keep ".git/ (all git history preserved)"

echo ""
echo "📊 SUMMARY:"
echo "───────────"
echo "• Files removed: ~35 complex files and directories"
echo "• Files renamed: 7 streamlined files become main files"
echo "• Files created: 3 new documentation files"
echo "• Repository size: Reduced by ~80%"
echo "• Complexity: Reduced by ~90%"

echo ""
echo "🎯 RESULT:"
echo "──────────"
echo "• Single service architecture (app/main.py)"
echo "• 5 lightweight dependencies (requirements.txt)"
echo "• Simple installation (install.sh)"
echo "• Clean documentation (README.md, INSTALLATION.md)"
echo "• No nginx, gunicorn, cron, or ML dependencies"

echo ""
echo "⚠️  WARNING:"
echo "─────────────"
echo "This will PERMANENTLY remove the complex version from the repository."
echo "The old files will be deleted from git history when you commit."
echo "Make sure you want to proceed with the streamlined version only."

echo ""
echo "🚀 To proceed:"
echo "──────────────"
echo "1. ./cleanup_repository.sh"
echo "2. git commit -m 'Streamline repository - keep only simple version'"
echo "3. git push origin main"

echo ""
echo "📋 To preview files that exist now:"
echo "───────────────────────────────────"
echo "ls -la app/"
echo "ls -la app/templates/"
echo "ls -la scripts/ 2>/dev/null || echo 'scripts/ directory'"
echo "ls -la config/ 2>/dev/null || echo 'config/ directory'"