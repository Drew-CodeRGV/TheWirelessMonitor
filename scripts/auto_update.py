#!/usr/bin/env python3
"""
Automated update checker and installer
Runs every 8 hours to check for and install updates
"""

import sys
import os

# Add the user's rss_aggregator directory to Python path
user_home = os.path.expanduser("~")
sys.path.append(os.path.join(user_home, 'rss_aggregator'))

from app.updater import SystemUpdater
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        logging.info("Starting automated update check...")
        
        updater = SystemUpdater()
        
        # Check for updates
        update_info = updater.check_for_updates()
        
        if update_info.get('update_available', False):
            logging.info(f"Update available: {update_info.get('current_version')} -> {update_info.get('latest_version')}")
            
            # Perform update
            result = updater.perform_update()
            
            if result.get('success', False):
                logging.info("Automated update completed successfully")
            else:
                logging.error(f"Automated update failed: {result.get('error', 'Unknown error')}")
        else:
            logging.info("System is up to date")
            
    except Exception as e:
        logging.error(f"Error in automated update: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()