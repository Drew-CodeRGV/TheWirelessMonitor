#!/usr/bin/env python3
"""
Run newsletter monitor with credentials from .env file
This is more secure than hardcoding credentials
"""

import os
from email_newsletter_monitor import EmailNewsletterMonitor

# Try to load from .env file
try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
except FileNotFoundError:
    print("⚠️  .env file not found. Using default values.")
    print("   Create .env file from .env.example for secure credential storage.")
    print()

# Get credentials from environment
email_address = os.getenv('EMAIL_ADDRESS', 'wifinewsletters@gmail.com')
password = os.getenv('EMAIL_PASSWORD', '')
imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
check_interval = int(os.getenv('CHECK_INTERVAL', '30'))

print("=" * 60)
print("Email Newsletter Monitor")
print("=" * 60)
print()
print(f"📧 Email: {email_address}")
print(f"🌐 Server: {imap_server}")
print(f"⏱️  Interval: {check_interval} minutes")
print()

if not password:
    print("❌ ERROR: No password configured!")
    print()
    print("Please either:")
    print("1. Create .env file with EMAIL_PASSWORD (recommended)")
    print("2. Set EMAIL_PASSWORD environment variable")
    print()
    print("See setup_gmail_access.md for instructions.")
    exit(1)

# Create and run monitor
monitor = EmailNewsletterMonitor(email_address, password, imap_server)

print("Testing connection...")
if not monitor.connect():
    print()
    print("❌ Connection failed!")
    print()
    print("Troubleshooting:")
    print("1. Get App Password from: https://myaccount.google.com/apppasswords")
    print("2. Enable IMAP in Gmail settings")
    print("3. Update EMAIL_PASSWORD in .env file")
    print()
    print("See setup_gmail_access.md for detailed instructions.")
    exit(1)

monitor.disconnect()
print("✅ Connection successful!")
print()

# Ask for mode
print("Select mode:")
print("1. One-time check")
print("2. Continuous monitoring")
print()

mode = input("Enter choice (1 or 2, default 1): ").strip() or '1'

if mode == '2':
    print()
    print(f"Starting continuous monitoring (checking every {check_interval} minutes)")
    print("Press Ctrl+C to stop")
    print()
    monitor.run_continuous(interval_minutes=check_interval)
else:
    print()
    print("Running one-time check...")
    print()
    articles_count = monitor.fetch_newsletters(limit=50)
    print()
    print("=" * 60)
    print(f"✅ Complete! Found {articles_count} new articles.")
    print("=" * 60)
    print()
    print("Articles are now available at: http://localhost:8080")
