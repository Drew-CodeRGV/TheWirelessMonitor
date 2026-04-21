#!/usr/bin/env python3
"""
Local development server for The Signal
Ensures clean startup with no template caching
"""

import os
import sys

# Set environment variables for development
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the app
from app.main import WirelessMonitor

if __name__ == '__main__':
    print("=" * 60)
    print("Starting The Signal - Local Development Server")
    print("=" * 60)
    print(f"Template folder: {os.path.abspath('app/templates')}")
    print(f"Database: {os.path.abspath('data/wireless_monitor.db')}")
    print("=" * 60)
    
    monitor = WirelessMonitor()
    
    # Disable template caching for development
    monitor.app.config['TEMPLATES_AUTO_RELOAD'] = True
    monitor.app.jinja_env.auto_reload = True
    monitor.app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    print("\n✅ Server starting on http://localhost:8080")
    print("📝 Modern UI: http://localhost:8080/?modern=true")
    print("📰 Classic UI: http://localhost:8080/?modern=false")
    print("\nPress Ctrl+C to stop\n")
    
    monitor.app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        use_reloader=True
    )
