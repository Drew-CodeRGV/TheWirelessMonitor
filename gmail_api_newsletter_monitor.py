#!/usr/bin/env python3
"""
Gmail API Newsletter Monitor for Wireless Monitor
Uses Gmail API instead of IMAP (works with all Gmail account types)
"""

import os
import base64
import sqlite3
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Required packages not installed!")
    print()
    print("Please install:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print()
    exit(1)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailAPINewsletterMonitor:
    """Monitor Gmail inbox using Gmail API and extract articles from newsletters"""
    
    def __init__(self, db_path='data/wireless_monitor.db', credentials_file='credentials.json'):
        """
        Initialize Gmail API monitor
        
        Args:
            db_path: Path to SQLite database
            credentials_file: Path to OAuth credentials JSON file
        """
        self.db_path = db_path
        self.credentials_file = credentials_file
        self.token_file = 'token.json'
        self.service = None
        
        # Newsletter patterns
        self.newsletter_patterns = [
            r'newsletter',
            r'digest',
            r'weekly',
            r'daily',
            r'roundup',
            r'briefing',
            r'update',
            r'bulletin'
        ]
        
        # Wi-Fi keywords
        self.wifi_keywords = [
            'wifi', 'wi-fi', 'wireless', '802.11', 'bluetooth', '5g', '6g', 'lte',
            'cellular', 'antenna', 'spectrum', 'frequency', 'band', 'router',
            'access point', 'mesh', 'networking', 'connectivity', 'broadband'
        ]
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing access token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    logger.error("Please download OAuth credentials from Google Cloud Console")
                    return False
                
                logger.info("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
            logger.info("Credentials saved")
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Successfully authenticated with Gmail API")
            return True
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            return False
    
    def is_newsletter(self, subject, sender):
        """Check if email is a newsletter"""
        text = (subject + ' ' + sender).lower()
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in self.newsletter_patterns)
    
    def extract_links_from_html(self, html_content):
        """Extract article links from HTML email content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            url = link['href']
            text = link.get_text(strip=True)
            
            # Skip common non-article links
            if any(skip in url.lower() for skip in ['unsubscribe', 'preferences', 'facebook', 'twitter', 'linkedin', 'instagram']):
                continue
            
            if url.startswith('http') and not any(ext in url.lower() for ext in ['.jpg', '.png', '.gif', '.jpeg']):
                links.append({
                    'url': url,
                    'title': text[:200] if text else 'Untitled',
                    'description': ''
                })
        
        return links
    
    def calculate_relevance_score(self, title, description, url):
        """Calculate relevance score for article"""
        text = (title + ' ' + description + ' ' + url).lower()
        keyword_count = sum(1 for keyword in self.wifi_keywords if keyword in text)
        
        if keyword_count == 0:
            return 0.0
        elif keyword_count == 1:
            return 0.3
        elif keyword_count == 2:
            return 0.5
        else:
            return 0.7
    
    def get_or_create_newsletter_feed(self, newsletter_name, sender_email):
        """Get or create a feed entry for this newsletter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM rss_feeds WHERE url = ?', (sender_email,))
        result = cursor.fetchone()
        
        if result:
            feed_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO rss_feeds (name, url, active, last_fetched)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ''', (newsletter_name, sender_email))
            feed_id = cursor.lastrowid
            logger.info(f"Created new newsletter feed: {newsletter_name}")
        
        conn.commit()
        conn.close()
        return feed_id
    
    def save_article(self, feed_id, article):
        """Save article to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM articles WHERE url = ?', (article['url'],))
            if cursor.fetchone():
                conn.close()
                return False
            
            relevance_score = self.calculate_relevance_score(
                article['title'], 
                article['description'], 
                article['url']
            )
            
            cursor.execute('''
                INSERT INTO articles (feed_id, title, url, description, published_date, relevance_score, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, CURRENT_TIMESTAMP)
            ''', (
                feed_id,
                article['title'],
                article['url'],
                article['description'],
                relevance_score
            ))
            
            conn.commit()
            logger.info(f"Saved article: {article['title'][:50]} (score: {relevance_score:.2f})")
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            conn.close()
            return False
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            conn.close()
            return False
    
    def process_message(self, message_id):
        """Process a single Gmail message"""
        try:
            # Get message details
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            
            # Check if newsletter
            if not self.is_newsletter(subject, sender):
                return 0
            
            logger.info(f"Processing newsletter: {subject[:50]}...")
            
            # Extract sender email
            sender_match = re.search(r'<(.+?)>', sender)
            sender_email = sender_match.group(1) if sender_match else sender
            
            # Get or create feed
            feed_id = self.get_or_create_newsletter_feed(subject, sender_email)
            
            # Extract email body
            articles = []
            
            def get_body(payload):
                """Recursively extract email body"""
                if 'parts' in payload:
                    for part in payload['parts']:
                        get_body(part)
                else:
                    if payload.get('mimeType') == 'text/html':
                        data = payload.get('body', {}).get('data', '')
                        if data:
                            html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            articles.extend(self.extract_links_from_html(html))
            
            get_body(message['payload'])
            
            # Save articles
            saved_count = 0
            for article in articles:
                if self.save_article(feed_id, article):
                    saved_count += 1
            
            logger.info(f"Saved {saved_count} articles from: {subject[:50]}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")
            return 0
    
    def fetch_newsletters(self, max_results=50):
        """Fetch and process newsletters from Gmail"""
        if not self.service:
            if not self.authenticate():
                return 0
        
        try:
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q='is:unread'  # Only unread messages
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No unread messages found")
                return 0
            
            logger.info(f"Found {len(messages)} unread messages")
            
            total_articles = 0
            for message in messages:
                articles_count = self.process_message(message['id'])
                total_articles += articles_count
            
            logger.info(f"Total articles saved: {total_articles}")
            return total_articles
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return 0
    
    def run_continuous(self, interval_minutes=30):
        """Run continuously, checking for new newsletters"""
        logger.info(f"Starting continuous monitoring (checking every {interval_minutes} minutes)")
        
        while True:
            try:
                logger.info("Checking for new newsletters...")
                articles_count = self.fetch_newsletters()
                logger.info(f"Check complete. Found {articles_count} new articles.")
                
                logger.info(f"Waiting {interval_minutes} minutes until next check...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopping newsletter monitor...")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(60)


def main():
    """Main function"""
    import sys
    
    # Check if running as service (no terminal)
    if not sys.stdin.isatty():
        # Non-interactive mode - run continuously
        print("Running in non-interactive mode (systemd service)")
        monitor = GmailAPINewsletterMonitor()
        monitor.run_continuous(interval_minutes=10)
        return
    
    # Interactive mode
    print("=" * 60)
    print("Gmail API Newsletter Monitor")
    print("=" * 60)
    print()
    
    monitor = GmailAPINewsletterMonitor()
    
    print("Select mode:")
    print("1. One-time check")
    print("2. Continuous monitoring")
    print()
    
    mode = input("Enter choice (1 or 2, default 1): ").strip() or '1'
    
    if mode == '2':
        interval = input("Check interval in minutes (default 30): ").strip()
        interval = int(interval) if interval else 30
        monitor.run_continuous(interval_minutes=interval)
    else:
        print()
        print("Fetching newsletters...")
        articles_count = monitor.fetch_newsletters()
        print()
        print(f"✅ Complete! Found {articles_count} new articles.")


if __name__ == '__main__':
    main()
