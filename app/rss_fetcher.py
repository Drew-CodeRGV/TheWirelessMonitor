#!/usr/bin/env python3
"""
RSS Feed Fetcher
"""

import feedparser
import requests
from datetime import datetime, timedelta
from models import get_db_connection
import logging
from newspaper import Article
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RSS-Aggregator/1.0)'
        })
    
    def fetch_feed(self, feed_url, feed_id):
        """Fetch articles from a single RSS feed"""
        try:
            logger.info(f"Fetching feed: {feed_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            conn = get_db_connection()
            new_articles = []
            
            for entry in feed.entries:
                # Check if article already exists
                existing = conn.execute(
                    'SELECT id FROM articles WHERE url = ?', 
                    (entry.link,)
                ).fetchone()
                
                if existing:
                    continue
                
                # Extract article details
                title = entry.get('title', 'No Title')
                url = entry.get('link', '')
                description = entry.get('summary', '')
                
                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                else:
                    published_date = datetime.now()
                
                # Skip articles older than 7 days
                if published_date < datetime.now() - timedelta(days=7):
                    continue
                
                # Try to extract full content and image
                content, image_url = self.extract_article_content(url)
                
                # Insert article
                cursor = conn.execute('''
                    INSERT INTO articles 
                    (feed_id, title, url, description, content, published_date, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (feed_id, title, url, description, content, published_date, image_url))
                
                new_articles.append(cursor.lastrowid)
                logger.info(f"Added article: {title}")
                
                # Rate limiting
                time.sleep(0.5)
            
            # Update feed last_fetched timestamp
            conn.execute('''
                UPDATE rss_feeds SET last_fetched = CURRENT_TIMESTAMP WHERE id = ?
            ''', (feed_id,))
            
            conn.commit()
            conn.close()
            
            return new_articles
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {str(e)}")
            return []
    
    def extract_article_content(self, url):
        """Extract full article content and image using newspaper3k"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            content = article.text if article.text else ""
            image_url = article.top_image if article.top_image else ""
            
            return content, image_url
            
        except Exception as e:
            logger.warning(f"Could not extract content from {url}: {str(e)}")
            return "", ""
    
    def fetch_all_feeds(self):
        """Fetch articles from all active RSS feeds"""
        conn = get_db_connection()
        feeds = conn.execute('''
            SELECT id, name, url FROM rss_feeds WHERE active = 1
        ''').fetchall()
        conn.close()
        
        all_new_articles = []
        
        for feed in feeds:
            logger.info(f"Processing feed: {feed['name']}")
            new_articles = self.fetch_feed(feed['url'], feed['id'])
            all_new_articles.extend(new_articles)
            
            # Rate limiting between feeds
            time.sleep(2)
        
        logger.info(f"Total new articles fetched: {len(all_new_articles)}")
        return all_new_articles