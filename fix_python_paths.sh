#!/bin/bash

# Fix Python Path Issues in The Wireless Monitor
# Run this script if you get import errors during daily_fetch.py execution

set -e

echo "🔧 Fixing Python path issues..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Determine installation directory
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)
INSTALL_DIR="$USER_HOME/rss_aggregator"

if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Installation directory not found: $INSTALL_DIR"
    print_error "Please run the main installation script first"
    exit 1
fi

cd $INSTALL_DIR

print_status "Fixing daily_fetch.py script..."
cat > scripts/daily_fetch.py << 'EOF'
#!/usr/bin/env python3
"""
Daily RSS fetch and analysis script
"""
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from app.rss_fetcher import RSSFetcher
from app.ai_analyzer import AIAnalyzer
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        logging.info("Starting daily RSS fetch...")
        
        # Fetch RSS feeds
        fetcher = RSSFetcher()
        new_articles = fetcher.fetch_all_feeds()
        
        # Analyze articles
        analyzer = AIAnalyzer()
        analyzed_count = analyzer.analyze_articles(new_articles)
        
        logging.info(f"Completed: {len(new_articles)} fetched, {analyzed_count} analyzed")
        
    except Exception as e:
        logging.error(f"Error in daily fetch: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/daily_fetch.py

print_status "Fixing weekly_digest.py script..."
cat > scripts/weekly_digest.py << 'EOF'
#!/usr/bin/env python3
"""
Weekly digest generation script
"""
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from app.ai_analyzer import AIAnalyzer
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        logging.info("Generating weekly digest...")
        
        analyzer = AIAnalyzer()
        digest = analyzer.generate_weekly_digest()
        
        logging.info("Weekly digest generated successfully")
        
    except Exception as e:
        logging.error(f"Error generating weekly digest: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/weekly_digest.py

print_status "Updating cron jobs with correct PYTHONPATH..."
# Remove old cron jobs
crontab -l 2>/dev/null | grep -v "rss_aggregator\|RSS Aggregator" | crontab -

# Add new cron jobs with correct paths
(crontab -l 2>/dev/null; echo "# RSS Aggregator automated tasks") | crontab -
(crontab -l 2>/dev/null; echo "0 */6 * * * cd $INSTALL_DIR && PYTHONPATH=$INSTALL_DIR ./venv/bin/python scripts/daily_fetch.py >> logs/cron.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 8 * * 1 cd $INSTALL_DIR && PYTHONPATH=$INSTALL_DIR ./venv/bin/python scripts/weekly_digest.py >> logs/cron.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 */8 * * * cd $INSTALL_DIR && PYTHONPATH=$INSTALL_DIR ./venv/bin/python scripts/auto_update.py >> logs/update.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "*/15 * * * * $INSTALL_DIR/scripts/monitor.sh >> logs/monitor.log 2>&1") | crontab -

print_success "✅ Python path issues fixed!"

print_status "Testing the fix..."
source venv/bin/activate
if PYTHONPATH=$INSTALL_DIR python3 scripts/daily_fetch.py; then
    print_success "✅ daily_fetch.py is working correctly!"
else
    print_warning "There may still be some issues. Check the error messages above."
fi

echo ""
echo "The scripts should now work correctly with proper Python paths."
echo "You can test manually with:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  PYTHONPATH=$INSTALL_DIR python3 scripts/daily_fetch.py"