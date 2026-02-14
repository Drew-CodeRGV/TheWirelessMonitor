#!/usr/bin/env python3
"""
Email Newsletter Monitor for Wireless Monitor
Monitors an email inbox and extracts articles from newsletters
"""

import imaplib
import email
from email.header import decode_header
import sqlite3
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailNewsletterMonitor:
    """Monitor email inbox for newsletters and extract articles"""
    
    def __init__(self, email_address, password, imap_server, db_path='data/wireless_monitor.db'):
        """
        Initialize email monitor
        
        Args:
            email_address: Email address to monitor
            password: Email password or app-specific password
            imap_server: IMAP server address (e.g., 'imap.gmail.com')
            db_path: Path to SQLite database
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.db_path = db_path
        self.mail = None
        
        # Newsletter patterns to identify newsletter emails
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
        
        # Wi-Fi keywords for relevance filtering
        self.wifi_keywords = [
            'wifi', 'wi-fi', 'wireless', '802.11', 'bluetooth', '5g', '6g', 'lte',
            'cellular', 'antenna', 'spectrum', 'frequency', 'band', 'router',
            'access point', 'mesh', 'networking', 'connectivity', 'broadband'
        ]
    
    def connect(self):
        """Connect to email server"""
        try:
            logger.info(f"Connecting to {self.imap_server}...")
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.password)
            logger.info("Successfully connected to email server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from email server"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
                logger.info("Disconnected from email server")
            except:
                pass
    
    def is_newsletter(self, subject, sender):
        """Check if email is a newsletter"""
        text = (subject + ' ' + sender).lower()
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in self.newsletter_patterns)
    
    def decode_email_subject(self, subject):
        """Decode email subject"""
        if subject is None:
            return ""
        
        decoded_parts = decode_header(subject)
        decoded_subject = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_subject += part.decode(encoding or 'utf-8', errors='ignore')
                except:
                    decoded_subject += part.decode('utf-8', errors='ignore')
            else:
                decoded_subject += str(part)
        
        return decoded_subject
    
    def extract_links_from_html(self, html_content):
        """Extract article links from HTML email content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            url = link['href']
            text = link.get_text(strip=True)
            
            # Skip common non-article links
            if any(skip in url.lower() for skip in ['unsubscribe', 'preferences', 'facebook', 'twitter', 'linkedin', 'instagram']):
                continue
            
            # Skip tracking pixels and images
            if url.startswith('http') and not any(ext in url.lower() for ext in ['.jpg', '.png', '.gif', '.jpeg']):
                links.append({
                    'url': url,
                    'title': text[:200] if text else 'Untitled',
                    'description': ''
                })
        
        return links
    
    def extract_articles_from_text(self, text_content):
        """Extract article links from plain text email"""
        links = []
        
        # Find URLs in text
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text_content)
        
        for url in urls:
            # Skip common non-article links
            if any(skip in url.lower() for skip in ['unsubscribe', 'preferences', 'facebook.com', 'twitter.com', 'linkedin.com']):
                continue
            
            links.append({
                'url': url,
                'title': 'Article from newsletter',
                'description': ''
            })
        
        return links
    
    def calculate_relevance_score(self, title, description, url):
        """Calculate relevance score for article"""
        text = (title + ' ' + description + ' ' + url).lower()
        
        # Count keyword matches
        keyword_count = sum(1 for keyword in self.wifi_keywords if keyword in text)
        
        # Calculate score (0-1 range)
        if keyword_count == 0:
            return 0.0
        elif keyword_count == 1:
            return 0.3
        elif keyword_count == 2:
            return 0.5
        elif keyword_count >= 3:
            return 0.7
        
        return 0.0
    
    def get_or_create_newsletter_feed(self, newsletter_name, sender_email):
        """Get or create a feed entry for this newsletter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if feed exists
        cursor.execute('SELECT id FROM rss_feeds WHERE url = ?', (sender_email,))
        result = cursor.fetchone()
        
        if result:
            feed_id = result[0]
        else:
            # Create new feed
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
            # Check if article already exists
            cursor.execute('SELECT id FROM articles WHERE url = ?', (article['url'],))
            if cursor.fetchone():
                logger.debug(f"Article already exists: {article['title'][:50]}")
                conn.close()
                return False
            
            # Calculate relevance score
            relevance_score = self.calculate_relevance_score(
                article['title'], 
                article['description'], 
                article['url']
            )
            
            # Insert article
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
            logger.debug(f"Duplicate article: {article['title'][:50]}")
            conn.close()
            return False
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            conn.close()
            return False
    
    def process_email(self, email_id):
        """Process a single email and extract articles"""
        try:
            # Fetch email
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return 0
            
            # Parse email
            email_body = msg_data[0][1]
            message = email.message_from_bytes(email_body)
            
            # Get subject and sender
            subject = self.decode_email_subject(message['subject'])
            sender = message['from']
            
            # Check if it's a newsletter
            if not self.is_newsletter(subject, sender):
                return 0
            
            logger.info(f"Processing newsletter: {subject[:50]}...")
            
            # Extract sender email
            sender_match = re.search(r'<(.+?)>', sender)
            sender_email = sender_match.group(1) if sender_match else sender
            
            # Get or create feed for this newsletter
            feed_id = self.get_or_create_newsletter_feed(subject, sender_email)
            
            # Extract articles from email body
            articles = []
            
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == 'text/html':
                        try:
                            html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            articles.extend(self.extract_links_from_html(html_content))
                        except:
                            pass
                    elif content_type == 'text/plain':
                        try:
                            text_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            articles.extend(self.extract_articles_from_text(text_content))
                        except:
                            pass
            else:
                content_type = message.get_content_type()
                
                if content_type == 'text/html':
                    html_content = message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    articles.extend(self.extract_links_from_html(html_content))
                elif content_type == 'text/plain':
                    text_content = message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    articles.extend(self.extract_articles_from_text(text_content))
            
            # Save articles
            saved_count = 0
            for article in articles:
                if self.save_article(feed_id, article):
                    saved_count += 1
            
            logger.info(f"Saved {saved_count} articles from newsletter: {subject[:50]}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return 0
    
    def fetch_newsletters(self, folder='INBOX', limit=50):
        """Fetch and process newsletters from inbox"""
        if not self.connect():
            return 0
        
        try:
            # Select mailbox
            self.mail.select(folder)
            
            # Search for unread emails (or all recent emails)
            # Use 'ALL' to get all emails, or 'UNSEEN' for unread only
            status, messages = self.mail.search(None, 'ALL')
            
            if status != 'OK':
                logger.error("Failed to search emails")
                return 0
            
            # Get email IDs
            email_ids = messages[0].split()
            
            # Process most recent emails (limit)
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            logger.info(f"Found {len(email_ids)} emails to process")
            
            total_articles = 0
            for email_id in email_ids:
                articles_count = self.process_email(email_id)
                total_articles += articles_count
            
            logger.info(f"Total articles saved: {total_articles}")
            return total_articles
            
        except Exception as e:
            logger.error(f"Error fetching newsletters: {e}")
            return 0
        finally:
            self.disconnect()
    
    def run_continuous(self, interval_minutes=30):
        """Run continuously, checking for new newsletters at intervals"""
        logger.info(f"Starting continuous monitoring (checking every {interval_minutes} minutes)")
        
        while True:
            try:
                logger.info("Checking for new newsletters...")
                articles_count = self.fetch_newsletters()
                logger.info(f"Check complete. Found {articles_count} new articles.")
                
                # Wait for next check
                logger.info(f"Waiting {interval_minutes} minutes until next check...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopping newsletter monitor...")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


def main():
    """Main function for standalone execution"""
    import sys
    
    print("=" * 60)
    print("Email Newsletter Monitor for Wireless Monitor")
    print("=" * 60)
    print()
    
    # Get email credentials
    if len(sys.argv) >= 4:
        email_address = sys.argv[1]
        password = sys.argv[2]
        imap_server = sys.argv[3]
    else:
        print("Usage: python email_newsletter_monitor.py <email> <password> <imap_server>")
        print()
        print("Example:")
        print("  python email_newsletter_monitor.py user@gmail.com 'app_password' imap.gmail.com")
        print()
        print("Common IMAP servers:")
        print("  Gmail: imap.gmail.com")
        print("  Outlook: outlook.office365.com")
        print("  Yahoo: imap.mail.yahoo.com")
        print()
        
        # Interactive mode
        email_address = input("Enter email address: ").strip()
        password = input("Enter password (or app-specific password): ").strip()
        imap_server = input("Enter IMAP server (e.g., imap.gmail.com): ").strip()
    
    if not email_address or not password or not imap_server:
        print("Error: All fields are required")
        sys.exit(1)
    
    # Create monitor
    monitor = EmailNewsletterMonitor(email_address, password, imap_server)
    
    # Ask for mode
    print()
    print("Select mode:")
    print("1. One-time check")
    print("2. Continuous monitoring")
    
    mode = input("Enter choice (1 or 2): ").strip()
    
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
