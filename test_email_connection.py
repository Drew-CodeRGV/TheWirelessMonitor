#!/usr/bin/env python3
"""Test email connection and fetch newsletters"""

from email_newsletter_monitor import EmailNewsletterMonitor

# Your credentials
email_address = "wifinewsletters@gmail.com"
password = "Admin$123#"
imap_server = "imap.gmail.com"

print("=" * 60)
print("Testing Email Newsletter Monitor")
print("=" * 60)
print()
print(f"Email: {email_address}")
print(f"Server: {imap_server}")
print()

# Create monitor
monitor = EmailNewsletterMonitor(email_address, password, imap_server)

# Test connection
print("Testing connection...")
if monitor.connect():
    print("✅ Connection successful!")
    monitor.disconnect()
    print()
    
    # Fetch newsletters
    print("Fetching newsletters (one-time check)...")
    print()
    articles_count = monitor.fetch_newsletters(limit=50)
    print()
    print("=" * 60)
    print(f"✅ Complete! Found {articles_count} new articles.")
    print("=" * 60)
else:
    print("❌ Connection failed!")
    print()
    print("Troubleshooting:")
    print("1. Check if IMAP is enabled in Gmail settings")
    print("2. If using 2FA, create an App Password:")
    print("   - Go to Google Account → Security → App passwords")
    print("   - Generate password for 'Mail' app")
    print("   - Use that password instead")
    print("3. Check for typos in email/password")
