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
from urllib.parse import urlparse

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
        
        # Add template functions
        self.setup_template_functions()
        
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
        
        # Add new columns if they don't exist (for existing databases)
        try:
            conn.execute('ALTER TABLE articles ADD COLUMN content TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            conn.execute('ALTER TABLE articles ADD COLUMN wifi_keywords TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
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
                ('Ars Technica Technology', 'https://feeds.arstechnica.com/arstechnica/technology-lab'),
                ('TechCrunch', 'https://techcrunch.com/feed/'),
                ('The Verge', 'https://www.theverge.com/rss/index.xml'),
                ('IEEE Spectrum', 'https://spectrum.ieee.org/rss'),
                ('Fierce Wireless', 'https://www.fiercewireless.com/rss/xml'),
                ('RCR Wireless News', 'https://www.rcrwireless.com/feed'),
                ('Wi-Fi Alliance News', 'https://www.wi-fi.org/news-events/newsroom/rss'),
                ('Wireless Week', 'https://www.wirelessweek.com/rss.xml'),
            ]
            
            for name, url in default_feeds:
                try:
                    conn.execute('INSERT INTO rss_feeds (name, url) VALUES (?, ?)', (name, url))
                    logger.info(f"Added default feed: {name}")
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
            
            # Get view mode from query parameter (default to newspaper)
            view_mode = request.args.get('view', 'newspaper')
            show_all = request.args.get('show_all', 'false').lower() == 'true'
            
            # Get today's top stories
            today = datetime.now().strftime('%Y-%m-%d')
            
            if show_all:
                # Show all articles regardless of relevance
                stories = conn.execute('''
                    SELECT a.*, f.name as feed_name, f.url as feed_url
                    FROM articles a 
                    JOIN rss_feeds f ON a.feed_id = f.id
                    WHERE DATE(a.published_date) = ?
                    ORDER BY a.relevance_score DESC, a.published_date DESC
                    LIMIT 100
                ''', (today,)).fetchall()
                
                # Get recent stories if no stories today
                if not stories:
                    stories = conn.execute('''
                        SELECT a.*, f.name as feed_name, f.url as feed_url
                        FROM articles a 
                        JOIN rss_feeds f ON a.feed_id = f.id
                        WHERE DATE(a.published_date) >= DATE('now', '-3 days')
                        ORDER BY a.relevance_score DESC, a.published_date DESC
                        LIMIT 100
                    ''').fetchall()
            else:
                # Show only relevant articles (score > 0.3)
                stories = conn.execute('''
                    SELECT a.*, f.name as feed_name, f.url as feed_url
                    FROM articles a 
                    JOIN rss_feeds f ON a.feed_id = f.id
                    WHERE DATE(a.published_date) = ? AND a.relevance_score > 0.3
                    ORDER BY a.relevance_score DESC, a.published_date DESC
                    LIMIT 20
                ''', (today,)).fetchall()
                
                # Get recent stories if no stories today
                if not stories:
                    stories = conn.execute('''
                        SELECT a.*, f.name as feed_name, f.url as feed_url
                        FROM articles a 
                        JOIN rss_feeds f ON a.feed_id = f.id
                        WHERE DATE(a.published_date) >= DATE('now', '-3 days') AND a.relevance_score > 0.3
                        ORDER BY a.relevance_score DESC, a.published_date DESC
                        LIMIT 20
                    ''').fetchall()
            
            # Get total article count for today
            total_today = conn.execute('SELECT COUNT(*) FROM articles WHERE DATE(published_date) = ?', (today,)).fetchone()[0]
            if total_today == 0:
                total_today = conn.execute('SELECT COUNT(*) FROM articles WHERE DATE(published_date) >= DATE("now", "-3 days")').fetchone()[0]
            
            conn.close()
            return render_template('index.html', stories=stories, date=today, view_mode=view_mode, show_all=show_all, total_articles=total_today)
        
        @self.app.route('/feeds')
        def manage_feeds():
            conn = self.get_db_connection()
            feeds = conn.execute('SELECT * FROM rss_feeds ORDER BY name').fetchall()
            view_mode = request.args.get('view', 'newspaper')
            conn.close()
            return render_template('feeds.html', feeds=feeds, view_mode=view_mode)
        
        @self.app.route('/add_feed', methods=['POST'])
        def add_feed():
            name = request.form['name']
            url = request.form['url']
            view_mode = request.args.get('view', 'newspaper')
            
            conn = self.get_db_connection()
            try:
                conn.execute('INSERT INTO rss_feeds (name, url, active) VALUES (?, ?, 1)', (name, url))
                conn.commit()
                flash(f'Successfully added feed: {name}', 'success')
            except sqlite3.IntegrityError:
                flash(f'Feed URL already exists: {url}', 'error')
            finally:
                conn.close()
            
            return redirect(url_for('manage_feeds', view=view_mode))
        
        @self.app.route('/add_google_news', methods=['POST'])
        def add_google_news():
            keyword = request.form['keyword'].strip()
            view_mode = request.args.get('view', 'newspaper')
            
            if not keyword:
                flash('Please enter a keyword', 'error')
                return redirect(url_for('manage_feeds', view=view_mode))
            
            # Create Google News RSS URL
            google_news_url = f"https://news.google.com/news/rss/search?q={keyword}&hl=en"
            feed_name = f"Google News: {keyword}"
            
            conn = self.get_db_connection()
            try:
                conn.execute('INSERT INTO rss_feeds (name, url, active) VALUES (?, ?, 1)', (feed_name, google_news_url))
                conn.commit()
                flash(f'Successfully added Google News feed for "{keyword}"', 'success')
            except sqlite3.IntegrityError:
                flash(f'Google News feed for "{keyword}" already exists', 'error')
            finally:
                conn.close()
            
            return redirect(url_for('manage_feeds', view=view_mode))
        
        @self.app.route('/bulk_import', methods=['POST'])
        def bulk_import():
            urls_text = request.form['urls']
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            view_mode = request.args.get('view', 'newspaper')
            
            conn = self.get_db_connection()
            added_count = 0
            error_count = 0
            
            for url in urls:
                try:
                    # Try to fetch the feed to get its title
                    response = requests.get(url, timeout=10)
                    parsed_feed = feedparser.parse(response.content)
                    
                    # Use feed title or fallback to domain name
                    if parsed_feed.feed.get('title'):
                        name = parsed_feed.feed.title
                    else:
                        # Extract domain name as fallback
                        domain = urlparse(url).netloc
                        name = domain.replace('www.', '').title()
                    
                    # Insert into database
                    conn.execute('INSERT INTO rss_feeds (name, url, active) VALUES (?, ?, 1)', (name, url))
                    added_count += 1
                    
                except sqlite3.IntegrityError:
                    error_count += 1  # URL already exists
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {e}")
                    error_count += 1
            
            conn.commit()
            conn.close()
            
            if added_count > 0:
                flash(f'Successfully added {added_count} RSS feeds', 'success')
            if error_count > 0:
                flash(f'{error_count} feeds could not be added (duplicates or invalid URLs)', 'error')
            
            return redirect(url_for('manage_feeds', view=view_mode))
        
        @self.app.route('/toggle_feed/<int:feed_id>')
        def toggle_feed(feed_id):
            conn = self.get_db_connection()
            conn.execute('UPDATE rss_feeds SET active = CASE WHEN active = 1 THEN 0 ELSE 1 END WHERE id = ?', (feed_id,))
            conn.commit()
            conn.close()
            view_mode = request.args.get('view', 'newspaper')
            return redirect(url_for('manage_feeds', view=view_mode))
        
        @self.app.route('/admin')
        def admin():
            conn = self.get_db_connection()
            stats = {
                'total_articles': conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0],
                'total_feeds': conn.execute('SELECT COUNT(*) FROM rss_feeds').fetchone()[0],
                'active_feeds': conn.execute('SELECT COUNT(*) FROM rss_feeds WHERE active = 1').fetchone()[0],
                'articles_today': conn.execute('SELECT COUNT(*) FROM articles WHERE DATE(published_date) = DATE("now")').fetchone()[0],
            }
            view_mode = request.args.get('view', 'newspaper')
            conn.close()
            return render_template('admin.html', stats=stats, view_mode=view_mode)
        
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
        
        @self.app.route('/api/update_system', methods=['POST'])
        def update_system():
            """Update system from GitHub repository"""
            try:
                import subprocess
                import os
                
                # Get current user and project directory
                current_user = os.getenv('USER', 'wifi')
                project_dir = f'/home/{current_user}/wireless_monitor'
                
                # First, stash any local changes
                stash_result = subprocess.run(['git', 'stash', 'push', '-m', 'Auto-stash before update'], 
                                            cwd=project_dir, 
                                            capture_output=True, 
                                            text=True, 
                                            timeout=30)
                
                # Pull latest changes
                result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                      cwd=project_dir, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=30)
                
                if result.returncode == 0:
                    # Try to restore stashed changes if there were any
                    if 'No local changes to save' not in stash_result.stdout:
                        # There were changes stashed, try to apply them
                        pop_result = subprocess.run(['git', 'stash', 'pop'], 
                                                  cwd=project_dir, 
                                                  capture_output=True, 
                                                  text=True, 
                                                  timeout=30)
                        
                        if pop_result.returncode != 0:
                            # Stash pop failed, keep the stash for manual resolution
                            message = f'Update successful but local changes were stashed. Check "git stash list" for your changes. {result.stdout}'
                        else:
                            message = f'Update successful and local changes restored. {result.stdout}'
                    else:
                        message = f'Update successful. {result.stdout}'
                    
                    # Restart service after update
                    subprocess.run(['sudo', 'systemctl', 'restart', 'wireless-monitor'], 
                                 timeout=10)
                    
                    return jsonify({
                        'success': True, 
                        'message': message
                    })
                else:
                    return jsonify({
                        'success': False, 
                        'error': f'Git pull failed: {result.stderr}'
                    })
                    
            except subprocess.TimeoutExpired:
                return jsonify({'success': False, 'error': 'Update timed out'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/insights')
        def insights():
            """AI-powered industry insights page"""
            view_mode = request.args.get('view', 'newspaper')
            
            conn = self.get_db_connection()
            
            # Get recent articles for analysis
            recent_articles = conn.execute('''
                SELECT a.*, f.name as feed_name 
                FROM articles a 
                JOIN rss_feeds f ON a.feed_id = f.id
                WHERE DATE(a.published_date) >= DATE('now', '-7 days')
                AND a.relevance_score > 0.2
                ORDER BY a.published_date DESC
                LIMIT 50
            ''').fetchall()
            
            # Get or generate AI insights
            insights_data = self.get_ai_insights(recent_articles)
            
            conn.close()
            return render_template('insights.html', insights=insights_data, view_mode=view_mode)
        
        @self.app.route('/api/refresh_insights', methods=['POST'])
        def refresh_insights():
            """Refresh AI insights"""
            try:
                conn = self.get_db_connection()
                
                # Get recent articles
                recent_articles = conn.execute('''
                    SELECT a.*, f.name as feed_name 
                    FROM articles a 
                    JOIN rss_feeds f ON a.feed_id = f.id
                    WHERE DATE(a.published_date) >= DATE('now', '-7 days')
                    AND a.relevance_score > 0.2
                    ORDER BY a.published_date DESC
                    LIMIT 50
                ''').fetchall()
                
                # Generate new insights
                insights_data = self.generate_ai_insights(recent_articles)
                
                # Store insights in database
                conn.execute('INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)', 
                           ('ai_insights', json.dumps(insights_data)))
                conn.commit()
                conn.close()
                
                return jsonify({'success': True, 'insights': insights_data})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/verify_feed/<int:feed_id>')
        def verify_feed(feed_id):
            """Verify if an RSS feed is working"""
            conn = self.get_db_connection()
            feed = conn.execute('SELECT * FROM rss_feeds WHERE id = ?', (feed_id,)).fetchone()
            conn.close()
            
            if not feed:
                return jsonify({'success': False, 'error': 'Feed not found'})
            
            try:
                response = requests.get(feed['url'], timeout=15)
                parsed_feed = feedparser.parse(response.content)
                
                if parsed_feed.bozo:
                    return jsonify({
                        'success': False, 
                        'error': f'Invalid RSS feed format: {parsed_feed.bozo_exception}'
                    })
                
                if not parsed_feed.entries:
                    return jsonify({
                        'success': False, 
                        'error': 'RSS feed contains no entries'
                    })
                
                return jsonify({
                    'success': True,
                    'title': parsed_feed.feed.get('title', 'Unknown'),
                    'description': parsed_feed.feed.get('description', 'No description'),
                    'entries_count': len(parsed_feed.entries),
                    'last_updated': parsed_feed.feed.get('updated', 'Unknown')
                })
                
            except requests.RequestException as e:
                return jsonify({'success': False, 'error': f'Network error: {str(e)}'})
            except Exception as e:
                return jsonify({'success': False, 'error': f'Parsing error: {str(e)}'})
        
        @self.app.route('/api/force_update_system', methods=['POST'])
        def force_update_system():
            """Force update system - discards all local changes"""
            try:
                import subprocess
                import os
                
                # Get current user and project directory
                current_user = os.getenv('USER', 'wifi')
                project_dir = f'/home/{current_user}/wireless_monitor'
                
                # Reset to remote state (discards all local changes)
                reset_result = subprocess.run(['git', 'reset', '--hard', 'origin/main'], 
                                            cwd=project_dir, 
                                            capture_output=True, 
                                            text=True, 
                                            timeout=30)
                
                if reset_result.returncode != 0:
                    return jsonify({
                        'success': False, 
                        'error': f'Git reset failed: {reset_result.stderr}'
                    })
                
                # Pull latest changes
                result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                      cwd=project_dir, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=30)
                
                if result.returncode == 0:
                    # Restart service after update
                    subprocess.run(['sudo', 'systemctl', 'restart', 'wireless-monitor'], 
                                 timeout=10)
                    
                    return jsonify({
                        'success': True, 
                        'message': 'System force updated successfully. All local changes discarded. Service restarting...'
                    })
                else:
                    return jsonify({
                        'success': False, 
                        'error': f'Git pull failed after reset: {result.stderr}'
                    })
                    
            except subprocess.TimeoutExpired:
                return jsonify({'success': False, 'error': 'Force update timed out'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/reset_system', methods=['POST'])
        def reset_system():
            """Reset system to fresh state - wipe all data and reinstall"""
            try:
                import subprocess
                import os
                
                # Get current user and project directory
                current_user = os.getenv('USER', 'wifi')
                project_dir = f'/home/{current_user}/wireless_monitor'
                reset_script = f'{project_dir}/reset_system.sh'
                
                # Run the reset script
                result = subprocess.run([reset_script], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=120)
                
                if result.returncode == 0:
                    return jsonify({
                        'success': True, 
                        'message': 'System reset completed. Service restarting...',
                        'output': result.stdout
                    })
                else:
                    return jsonify({
                        'success': False, 
                        'error': f'Reset failed: {result.stderr}'
                    })
                    
            except subprocess.TimeoutExpired:
                return jsonify({'success': False, 'error': 'Reset timed out'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
    
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
                    
                    # Clean up description/summary - remove HTML tags
                    description = entry.get('summary', entry.get('description', ''))
                    if description:
                        # Remove HTML tags and decode entities
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(description, 'html.parser')
                        description = soup.get_text().strip()
                        # Remove extra whitespace
                        description = ' '.join(description.split())
                    
                    # Try to get full content if available
                    content = ''
                    if hasattr(entry, 'content') and entry.content:
                        content_html = entry.content[0].value if isinstance(entry.content, list) else entry.content
                        soup = BeautifulSoup(content_html, 'html.parser')
                        content = soup.get_text().strip()
                        content = ' '.join(content.split())
                    
                    published = entry.get('published_parsed')
                    
                    if published:
                        published_date = datetime(*published[:6])
                    else:
                        published_date = datetime.now()
                    
                    # Calculate relevance score
                    text = f"{title} {description} {content}".lower()
                    relevance_score = self.calculate_relevance_score(text)
                    
                    # Extract keywords found for debugging
                    found_keywords = [kw for kw in self.wifi_keywords if kw in text]
                    keywords_str = ', '.join(found_keywords[:5])  # Store first 5 keywords found
                    
                    # Only store articles with some relevance
                    if relevance_score > 0.05:  # Lower threshold to capture more articles
                        conn.execute('''
                            INSERT INTO articles (feed_id, title, url, description, content, published_date, relevance_score, wifi_keywords)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (feed['id'], title, entry.link, description, content, published_date, relevance_score, keywords_str))
                        
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
    
    def get_ai_insights(self, articles):
        """Get AI insights from cache or generate new ones"""
        conn = self.get_db_connection()
        
        # Check if we have recent insights (less than 6 hours old)
        cached_insights = conn.execute('''
            SELECT value, updated_at FROM settings 
            WHERE key = "ai_insights" 
            AND datetime(updated_at) > datetime('now', '-6 hours')
        ''').fetchone()
        
        if cached_insights:
            conn.close()
            return json.loads(cached_insights['value'])
        
        # Generate new insights
        insights_data = self.generate_ai_insights(articles)
        
        # Cache the insights
        conn.execute('INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)', 
                   ('ai_insights', json.dumps(insights_data)))
        conn.commit()
        conn.close()
        
        return insights_data
    
    def generate_ai_insights(self, articles):
        """Generate AI insights from articles using pattern analysis"""
        if not articles:
            return self.get_default_insights()
        
        # Analyze articles for patterns and trends
        insights = {
            'whats_new': [],
            'whats_now': [],
            'whats_next': [],
            'generated_at': datetime.now().isoformat(),
            'articles_analyzed': len(articles)
        }
        
        # Keywords for different categories
        new_keywords = ['launch', 'announce', 'release', 'debut', 'unveil', 'introduce', 'new']
        now_keywords = ['adopt', 'deploy', 'implement', 'rollout', 'available', 'shipping']
        next_keywords = ['future', 'roadmap', 'plan', 'expect', 'predict', 'forecast', 'upcoming']
        
        # Technology categories
        tech_categories = {
            'Wi-Fi 6/6E/7': ['wifi 6', 'wi-fi 6', 'wifi 7', 'wi-fi 7', '802.11ax', '802.11be', '6ghz'],
            '5G/6G': ['5g', '6g', 'mmwave', 'sub-6', 'standalone', 'non-standalone'],
            'IoT/Edge': ['iot', 'edge computing', 'smart city', 'industrial iot', 'edge ai'],
            'Security': ['cybersecurity', 'zero trust', 'encryption', 'authentication', 'vpn'],
            'Enterprise': ['enterprise', 'business', 'corporate', 'workplace', 'hybrid work'],
            'Standards': ['ieee', 'standard', 'specification', 'protocol', 'certification']
        }
        
        # Analyze each article
        for article in articles:
            text = f"{article['title']} {article['description']}".lower()
            
            # Determine category
            category = None
            for cat, keywords in tech_categories.items():
                if any(keyword in text for keyword in keywords):
                    category = cat
                    break
            
            if not category:
                continue
            
            # Determine timeline (What's New/Now/Next)
            if any(keyword in text for keyword in new_keywords):
                timeline = 'whats_new'
            elif any(keyword in text for keyword in next_keywords):
                timeline = 'whats_next'
            elif any(keyword in text for keyword in now_keywords):
                timeline = 'whats_now'
            else:
                timeline = 'whats_now'  # Default
            
            # Create insight entry
            insight = {
                'title': article['title'],
                'summary': article['description'][:200] + '...' if len(article['description']) > 200 else article['description'],
                'category': category,
                'source': article['feed_name'],
                'url': article['url'],
                'relevance': article['relevance_score'],
                'published': article['published_date']
            }
            
            insights[timeline].append(insight)
        
        # Sort by relevance and limit results
        for timeline in ['whats_new', 'whats_now', 'whats_next']:
            insights[timeline] = sorted(insights[timeline], key=lambda x: x['relevance'], reverse=True)[:8]
        
        # Add trend analysis
        insights['trends'] = self.analyze_trends(articles)
        
        return insights
    
    def analyze_trends(self, articles):
        """Analyze trending topics and technologies"""
        trends = {}
        
        # Count mentions of key technologies
        tech_mentions = {
            'Wi-Fi 6/7': 0,
            '5G': 0,
            'IoT': 0,
            'Security': 0,
            'AI/ML': 0,
            'Cloud': 0
        }
        
        keywords_map = {
            'Wi-Fi 6/7': ['wifi 6', 'wi-fi 6', 'wifi 7', 'wi-fi 7', '802.11ax', '802.11be'],
            '5G': ['5g', 'mmwave', 'sub-6'],
            'IoT': ['iot', 'internet of things', 'smart'],
            'Security': ['security', 'cybersecurity', 'zero trust', 'encryption'],
            'AI/ML': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'Cloud': ['cloud', 'saas', 'paas', 'iaas']
        }
        
        for article in articles:
            text = f"{article['title']} {article['description']}".lower()
            for tech, keywords in keywords_map.items():
                if any(keyword in text for keyword in keywords):
                    tech_mentions[tech] += 1
        
        # Convert to trend format
        trends['technology_buzz'] = [
            {'name': tech, 'mentions': count, 'trend': 'up' if count > 2 else 'stable'}
            for tech, count in sorted(tech_mentions.items(), key=lambda x: x[1], reverse=True)
            if count > 0
        ]
        
        return trends
    
    def get_default_insights(self):
        """Return default insights when no articles are available"""
        return {
            'whats_new': [
                {
                    'title': 'Wi-Fi 7 Standard Finalization',
                    'summary': 'IEEE 802.11be (Wi-Fi 7) standard approaching final ratification with multi-link operation and 320MHz channels.',
                    'category': 'Standards',
                    'source': 'Industry Analysis',
                    'url': '#',
                    'relevance': 0.9,
                    'published': datetime.now().isoformat()
                }
            ],
            'whats_now': [
                {
                    'title': 'Enterprise Wi-Fi 6E Adoption Accelerating',
                    'summary': 'Organizations rapidly deploying Wi-Fi 6E for improved performance and reduced congestion in dense environments.',
                    'category': 'Enterprise',
                    'source': 'Market Research',
                    'url': '#',
                    'relevance': 0.8,
                    'published': datetime.now().isoformat()
                }
            ],
            'whats_next': [
                {
                    'title': 'Wi-Fi 8 Research and Development',
                    'summary': 'Early research into next-generation wireless technologies focusing on ultra-low latency and AI integration.',
                    'category': 'Future Tech',
                    'source': 'Research Preview',
                    'url': '#',
                    'relevance': 0.7,
                    'published': datetime.now().isoformat()
                }
            ],
            'trends': {
                'technology_buzz': [
                    {'name': 'Wi-Fi 6/7', 'mentions': 15, 'trend': 'up'},
                    {'name': '5G', 'mentions': 12, 'trend': 'up'},
                    {'name': 'Security', 'mentions': 8, 'trend': 'stable'}
                ]
            },
            'generated_at': datetime.now().isoformat(),
            'articles_analyzed': 0
        }
    
    def cleanup_old_articles(self):
        """Remove articles older than 30 days"""
        conn = self.get_db_connection()
        deleted = conn.execute('DELETE FROM articles WHERE published_date < DATE("now", "-30 days")').rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old articles")
    
    def setup_template_functions(self):
        """Setup template helper functions"""
        def get_feed_icon(feed_name, feed_url):
            """Get appropriate icon for feed source"""
            feed_name_lower = feed_name.lower()
            feed_url_lower = feed_url.lower()
            
            # Google News
            if 'google' in feed_name_lower or 'news.google.com' in feed_url_lower:
                return '🔍', '#4285f4'
            # Tech sites
            elif 'techcrunch' in feed_name_lower or 'techcrunch.com' in feed_url_lower:
                return '🚀', '#0f7b0f'
            elif 'verge' in feed_name_lower or 'theverge.com' in feed_url_lower:
                return '⚡', '#fa4b2a'
            elif 'ars technica' in feed_name_lower or 'arstechnica.com' in feed_url_lower:
                return '🔬', '#ff6600'
            elif 'ieee' in feed_name_lower or 'ieee.org' in feed_url_lower:
                return '⚙️', '#00629b'
            # Wireless specific
            elif 'wireless' in feed_name_lower or 'wi-fi' in feed_name_lower:
                return '📡', '#2980b9'
            elif 'mobile' in feed_name_lower or 'cellular' in feed_name_lower:
                return '📱', '#e74c3c'
            # Default
            else:
                return '📰', '#7f8c8d'
        
        # Make function available to templates
        self.app.jinja_env.globals['get_feed_icon'] = get_feed_icon
    
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
    monitor.run(port=8080)