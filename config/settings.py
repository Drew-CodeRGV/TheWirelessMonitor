#!/usr/bin/env python3
"""
Configuration settings for RSS News Aggregator
"""

import os
from datetime import timedelta

# Base configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Database
DATABASE_PATH = os.path.join(DATA_DIR, 'news.db')

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# RSS Fetching
RSS_FETCH_TIMEOUT = 30  # seconds
RSS_FETCH_INTERVAL = timedelta(hours=6)
MAX_ARTICLES_PER_FEED = 50
ARTICLE_MAX_AGE_DAYS = 30

# AI Analysis
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama2:7b-chat"
AI_ANALYSIS_TIMEOUT = 60  # seconds
MIN_RELEVANCE_SCORE = 0.3

# Wi-Fi/Wireless Keywords (expanded list)
WIFI_KEYWORDS = [
    # Core wireless technologies
    'wifi', 'wi-fi', 'wireless', '802.11', 'bluetooth', '5g', '6g', 'lte',
    'cellular', 'antenna', 'spectrum', 'frequency', 'band', 'router',
    'access point', 'mesh', 'networking', 'connectivity', 'broadband',
    'telecommunications', 'radio', 'signal', 'interference', 'latency',
    'bandwidth', 'throughput', 'beamforming', 'mimo', 'ofdm',
    
    # IoT and Smart Home
    'iot', 'internet of things', 'smart home', 'connected devices',
    'wireless charging', 'nfc', 'zigbee', 'thread', 'matter',
    'homekit', 'alexa', 'google home', 'smart speaker',
    
    # Security
    'wireless security', 'wpa3', 'wpa2', 'encryption', 'cybersecurity',
    'network security', 'authentication', 'vpn',
    
    # Industry terms
    'wireless industry', 'telecom', 'carrier', 'operator', 'infrastructure',
    'base station', 'cell tower', 'small cell', 'femtocell', 'picocell',
    'backhaul', 'fronthaul', 'edge computing', 'network slicing',
    
    # Standards and organizations
    'wi-fi alliance', 'ieee', '3gpp', 'fcc', 'etsi', 'itu',
    'wifi 6', 'wifi 6e', 'wifi 7', 'ax', 'ac', 'n',
    
    # Applications
    'autonomous vehicles', 'connected car', 'telemedicine',
    'remote work', 'video conferencing', 'streaming',
    'augmented reality', 'virtual reality', 'ar', 'vr',
    
    # Technical terms
    'modulation', 'coding', 'protocol', 'handover', 'roaming',
    'qos', 'quality of service', 'load balancing', 'optimization'
]

# Web interface
ITEMS_PER_PAGE = 20
CACHE_TIMEOUT = 300  # 5 minutes

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# System paths
PYTHON_PATH = '/home/pi/rss_aggregator/venv/bin/python'
SCRIPT_PATH = '/home/pi/rss_aggregator/scripts'

# Default RSS feeds for Wi-Fi/Wireless industry
DEFAULT_RSS_FEEDS = [
    {
        'name': 'Ars Technica',
        'url': 'https://feeds.arstechnica.com/arstechnica/index',
        'category': 'Technology News'
    },
    {
        'name': 'TechCrunch',
        'url': 'https://techcrunch.com/feed/',
        'category': 'Technology News'
    },
    {
        'name': 'The Verge',
        'url': 'https://www.theverge.com/rss/index.xml',
        'category': 'Technology News'
    },
    {
        'name': 'IEEE Spectrum',
        'url': 'https://spectrum.ieee.org/rss',
        'category': 'Engineering'
    },
    {
        'name': 'Wi-Fi Alliance News',
        'url': 'https://www.wi-fi.org/news-events/newsroom/rss',
        'category': 'Wi-Fi Industry'
    },
    {
        'name': 'Wireless Week',
        'url': 'https://www.wirelessweek.com/rss.xml',
        'category': 'Wireless Industry'
    },
    {
        'name': 'RCR Wireless',
        'url': 'https://www.rcrwireless.com/feed',
        'category': 'Wireless Industry'
    },
    {
        'name': 'Light Reading',
        'url': 'https://www.lightreading.com/rss_simple.asp',
        'category': 'Telecom'
    },
    {
        'name': 'Fierce Wireless',
        'url': 'https://www.fiercewireless.com/rss/xml',
        'category': 'Wireless Industry'
    },
    {
        'name': 'Mobile World Live',
        'url': 'https://www.mobileworldlive.com/feed/',
        'category': 'Mobile Industry'
    }
]

# Email notifications (optional)
ENABLE_EMAIL_NOTIFICATIONS = False
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', '')

# Performance settings
MAX_WORKERS = 4  # For concurrent processing
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds