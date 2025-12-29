#!/usr/bin/env python3
"""
Database models and initialization
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = '/home/pi/rss_aggregator/data/news.db'

def init_db():
    """Initialize the database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # RSS feeds table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rss_feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
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
            url TEXT NOT NULL UNIQUE,
            description TEXT,
            content TEXT,
            published_date TIMESTAMP,
            image_url TEXT,
            relevance_score REAL DEFAULT 0.0,
            entertainment_score REAL DEFAULT 0.0,
            wifi_keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (feed_id) REFERENCES rss_feeds (id)
        )
    ''')
    
    # Weekly digests table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS weekly_digests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start DATE,
            week_end DATE,
            summary TEXT,
            top_stories TEXT,
            podcast_script TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Update log table for system updates
    conn.execute('''
        CREATE TABLE IF NOT EXISTS update_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_from TEXT,
            version_to TEXT,
            update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success INTEGER DEFAULT 0,
            error_message TEXT
        )
    ''')
    
    # Social media configuration table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS social_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL UNIQUE,
            handle TEXT,
            display_name TEXT,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default social media platforms if none exist
    existing_social = conn.execute('SELECT COUNT(*) FROM social_config').fetchone()[0]
    if existing_social == 0:
        default_social = [
            ('twitter', '', 'Twitter/X', 1),
            ('linkedin', '', 'LinkedIn', 1),
            ('instagram', '', 'Instagram', 1),
            ('facebook', '', 'Facebook', 0),
            ('mastodon', '', 'Mastodon', 0)
        ]
        
        conn.executemany('''
            INSERT INTO social_config (platform, handle, display_name, enabled) 
            VALUES (?, ?, ?, ?)
        ''', default_social)
    
    # Insert default RSS feeds if none exist
    existing_feeds = conn.execute('SELECT COUNT(*) FROM rss_feeds').fetchone()[0]
    if existing_feeds == 0:
        default_feeds = [
            ('Ars Technica', 'https://feeds.arstechnica.com/arstechnica/index'),
            ('TechCrunch', 'https://techcrunch.com/feed/'),
            ('The Verge', 'https://www.theverge.com/rss/index.xml'),
            ('IEEE Spectrum', 'https://spectrum.ieee.org/rss'),
            ('Wi-Fi Alliance News', 'https://www.wi-fi.org/news-events/newsroom/rss'),
            ('Wireless Week', 'https://www.wirelessweek.com/rss.xml'),
            ('RCR Wireless', 'https://www.rcrwireless.com/feed'),
            ('Light Reading', 'https://www.lightreading.com/rss_simple.asp'),
        ]
        
        conn.executemany('''
            INSERT INTO rss_feeds (name, url) VALUES (?, ?)
        ''', default_feeds)
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn