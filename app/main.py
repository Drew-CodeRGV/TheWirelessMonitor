#!/usr/bin/env python3
"""
The Wireless Monitor - Simplified Single Service
All functionality in one streamlined application
"""

import os
import sys
import json
import sqlite3
import threading
import time
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Lightweight web framework
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
import feedparser
from bs4 import BeautifulSoup
import schedule

# Configure logging with better error handling
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Create handlers with error handling
handlers = [logging.StreamHandler()]
try:
    log_file = os.path.join(log_dir, 'app.log')
    # Ensure log file exists and is writable
    if not os.path.exists(log_file):
        open(log_file, 'a').close()
    handlers.append(logging.FileHandler(log_file))
except (PermissionError, OSError) as e:
    print(f"Warning: Could not create log file: {e}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

class WirelessMonitor:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'wireless-monitor-secret-key'
        self.db_path = 'data/wireless_monitor.db'
        self.running = True
        
        # Ensure directories exist
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Setup routes
        self.setup_routes()
        
        # Setup scheduler
        self.setup_scheduler()
        
        # Wi-Fi keywords for relevance scoring
        self.wifi_keywords = [
            'wifi', 'wi-fi', 'wireless', '802.11', 'bluetooth', '5g', '6g', 'lte',
            'cellular', 'antenna', 'spectrum', 'frequency', 'band', 'router',
            'access point', 'mesh', 'networking', 'connectivity', 'broadband',
            'telecommunications', 'radio', 'signal', 'interference', 'latency',
            'bandwidth', 'throughput', 'iot', 'internet of things', 'smart home'
        ]
    
    def init_database(self):
        """Initialize SQLite database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # RSS feeds table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS rss_feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                active INTEGER DEFAULT 1,
                last_fetched TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Articles table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                content TEXT,
                published_date TIMESTAMP,
                relevance_score REAL DEFAULT 0,
                entertainment_score REAL DEFAULT 0,
                wifi_keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES rss_feeds (id)
            )
        ''')
        
        # System settings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add default feeds if none exist
        feed_count = conn.execute('SELECT COUNT(*) FROM rss_feeds').fetchone()[0]
        if feed_count == 0:
            default_feeds = [
                ('Ars Technica', 'https://feeds.arstechnica.com/arstechnica/index'),
                ('TechCrunch', 'https://techcrunch.com/feed/'),
                ('The Verge', 'https://www.theverge.com/rss/index.xml'),
                ('IEEE Spectrum', 'https://spectrum.ieee.org/rss'),
                ('Fierce Wireless', 'https://www.fiercewireless.com/rss/xml'),
            ]
            
            for name, url in default_feeds:
                try:
                    conn.execute('INSERT INTO rss_feeds (name, url) VALUES (?, ?)', (name, url))
                except sqlite3.IntegrityError:
                    pass  # Feed already exists
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def get_db_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            conn = self.get_db_connection()
            
            # Get today's top stories
            today = datetime.now().strftime('%Y-%m-%d')
            stories = conn.execute('''
                SELECT * FROM articles 
                WHERE DATE(published_date) = ? AND relevance_score > 0.3
                ORDER BY relevance_score DESC, published_date DESC
                LIMIT 20
            ''', (today,)).fetchall()
            
            # Get recent stories if no stories today
            if not stories:
                stories = conn.execute('''
                    SELECT * FROM articles 
                    WHERE DATE(published_date) >= DATE('now', '-3 days') AND relevance_score > 0.3
                    ORDER BY relevance_score DESC, published_date DESC
                    LIMIT 20
                ''').fetchall()
            
            conn.close()
            return render_template('index.html', stories=stories, date=today)
        
        @self.app.route('/feeds')
        def manage_feeds():
            conn = self.get_db_connection()
            feeds = conn.execute('SELECT * FROM rss_feeds ORDER BY name').fetchall()
            conn.close()
            return render_template('feeds.html', feeds=feeds)
        
        @self.app.route('/add_feed', methods=['POST'])
        def add_feed():
            name = request.form['name']
            url = request.form['url']
            
            conn = self.get_db_connection()
            try:
                conn.execute('INSERT INTO rss_feeds (name, url, active) VALUES (?, ?, 1)', (name, url))
                conn.commit()
                flash(f'Successfully added feed: {name}', 'success')
            except sqlite3.IntegrityError:
                flash(f'Feed URL already exists: {url}', 'error')
            finally:
                conn.close()
            
            return redirect(url_for('manage_feeds'))
        
        @self.app.route('/toggle_feed/<int:feed_id>')
        def toggle_feed(feed_id):
            conn = self.get_db_connection()
            conn.execute('UPDATE rss_feeds SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE id = ?', (feed_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('manage_feeds'))
        
        @self.app.route('/admin')
        def admin():
            conn = self.get_db_connection()
            stats = {
                'total_articles': conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0],
                'total_feeds': conn.execute('SELECT COUNT(*) FROM rss_feeds').fetchone()[0],
                'active_feeds': conn.execute('SELECT COUNT(*) FROM rss_feeds WHERE active = 1').fetchone()[0],
                'articles_today': conn.execute('SELECT COUNT(*) FROM articles WHERE DATE(published_date) = DATE("now")').fetchone()[0],
            }
            conn.close()
            return render_template('admin.html', stats=stats)
        
        @self.app.route('/api/fetch_now')
        def fetch_now():
            try:
                count = self.fetch_rss_feeds()
                return jsonify({'success': True, 'fetched': count})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/status')
        def status():
            conn = self.get_db_connection()
            last_fetch = conn.execute('SELECT value FROM settings WHERE key = "last_fetch"').fetchone()
            conn.close()
            
            return jsonify({
                'status': 'running',
                'last_fetch': last_fetch['value'] if last_fetch else 'Never',
                'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
            })
    
    def fetch_rss_feeds(self):
        """Fetch and analyze RSS feeds"""
        logger.info("Starting RSS feed fetch...")
        
        conn = self.get_db_connection()
        feeds = conn.execute('SELECT * FROM rss_feeds WHERE active = 1').fetchall()
        
        total_new_articles = 0
        
        for feed in feeds:
            try:
                logger.info(f"Fetching feed: {feed['name']}")
                
                # Fetch RSS feed
                response = requests.get(feed['url'], timeout=30)
                parsed_feed = feedparser.parse(response.content)
                
                for entry in parsed_feed.entries[:20]:  # Limit to 20 most recent
                    # Check if article already exists
                    existing = conn.execute('SELECT id FROM articles WHERE url = ?', (entry.link,)).fetchone()
                    if existing:
                        continue
                    
                    # Extract article data
                    title = entry.get('title', 'No Title')
                    description = entry.get('summary', '')
                    published = entry.get('published_parsed')
                    
                    if published:
                        published_date = datetime(*published[:6])
                    else:
                        published_date = datetime.now()
                    
                    # Calculate relevance score
                    text = f"{title} {description}".lower()
                    relevance_score = self.calculate_relevance_score(text)
                    
                    # Only store articles with some relevance
                    if relevance_score > 0.1:
                        conn.execute('''
                            INSERT INTO articles (feed_id, title, url, description, published_date, relevance_score)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (feed['id'], title, entry.link, description, published_date, relevance_score))
                        
                        total_new_articles += 1
                
                # Update last fetched time
                conn.execute('UPDATE rss_feeds SET last_fetched = CURRENT_TIMESTAMP WHERE id = ?', (feed['id'],))
                
            except Exception as e:
                logger.error(f"Error fetching feed {feed['name']}: {e}")
        
        # Update global last fetch time
        conn.execute('INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)', 
                    ('last_fetch', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"RSS fetch completed: {total_new_articles} new articles")
        return total_new_articles
    
    def calculate_relevance_score(self, text):
        """Calculate relevance score based on Wi-Fi keywords"""
        keyword_matches = sum(1 for keyword in self.wifi_keywords if keyword in text)
        word_count = len(text.split())
        
        if word_count == 0:
            return 0
        
        # Calculate keyword density
        density = keyword_matches / word_count
        
        # Boost for important keywords
        important_keywords = ['wifi', 'wi-fi', 'wireless', '5g', '6g']
        important_matches = sum(1 for keyword in important_keywords if keyword in text)
        
        # Final score (0.0 to 1.0)
        base_score = min(density * 50, 0.8)  # Cap at 0.8
        importance_boost = min(important_matches * 0.1, 0.2)  # Up to 0.2 boost
        
        return min(base_score + importance_boost, 1.0)
    
    def cleanup_old_articles(self):
        """Remove articles older than 30 days"""
        conn = self.get_db_connection()
        deleted = conn.execute('DELETE FROM articles WHERE published_date < DATE("now", "-30 days")').rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old articles")
    
    def setup_scheduler(self):
        """Setup background task scheduler"""
        # Schedule RSS fetching every 6 hours
        schedule.every(6).hours.do(self.fetch_rss_feeds)
        
        # Schedule cleanup daily at 2 AM
        schedule.every().day.at("02:00").do(self.cleanup_old_articles)
        
        # Initial fetch
        threading.Thread(target=self.fetch_rss_feeds, daemon=True).start()
    
    def run_scheduler(self):
        """Run the background scheduler"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal, stopping...")
        self.running = False
    
    def run(self, host='0.0.0.0', port=5000):
        """Run the application"""
        self.start_time = time.time()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start background scheduler
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info(f"Starting The Wireless Monitor on {host}:{port}")
        
        try:
            self.app.run(host=host, port=port, debug=False, threaded=True)
        except KeyboardInterrupt:
            logger.info("Application stopped by user")
        finally:
            self.running = False

if __name__ == '__main__':
    monitor = WirelessMonitor()
    monitor.run()