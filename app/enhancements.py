"""
Wireless Monitor Enhancements Module

This module contains all enhancement features:
- Enhanced Image Scraper with multi-strategy extraction
- Social Media Monitor with API clients
- Wild Wi-Fi Curator with automatic scoring
- Social Event Discoverer

Author: Wireless Monitor Team
"""

import asyncio
import aiohttp
import sqlite3
import time
import json
import re
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Manages API rate limits for multiple platforms."""
    
    def __init__(self, db_path: str):
        """
        Initialize rate limiter.
        
        Args:
            db_path: Path to SQLite database for persistent state
        """
        self.db_path = db_path
        self.limits = {
            'twitter': {
                'user_timeline': (900, 900),  # (requests, seconds)
                'user_info': (900, 900)
            },
            'linkedin': {
                'profile_posts': (100, 86400),  # 100 per day
                'profile_info': (100, 86400)
            }
        }
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """Load rate limit state from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT platform, endpoint, request_count, window_start
            FROM rate_limit_state
        """)
        
        state = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'window_start': time.time()}))
        for row in cursor.fetchall():
            platform, endpoint, count, window_start = row
            state[platform][endpoint] = {'count': count, 'window_start': window_start}
        
        conn.close()
        return state
    
    def save_state(self):
        """Save rate limit state to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for platform, endpoints in self.state.items():
            for endpoint, data in endpoints.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO rate_limit_state
                    (platform, endpoint, request_count, window_start, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (platform, endpoint, data['count'], data['window_start']))
        
        conn.commit()
        conn.close()
    
    async def acquire(self, platform: str, endpoint: str):
        """
        Acquire permission to make an API request.
        
        Blocks if rate limit would be exceeded.
        
        Args:
            platform: Platform name (twitter, linkedin)
            endpoint: Endpoint name (user_timeline, profile_posts)
        """
        if platform not in self.limits or endpoint not in self.limits[platform]:
            return  # No limit configured
        
        max_requests, window_seconds = self.limits[platform][endpoint]
        current_state = self.state[platform][endpoint]
        
        # Check if window has expired
        elapsed = time.time() - current_state['window_start']
        if elapsed >= window_seconds:
            # Reset window
            current_state['count'] = 0
            current_state['window_start'] = time.time()
        
        # Check if limit reached
        if current_state['count'] >= max_requests:
            # Calculate wait time
            wait_time = window_seconds - elapsed
            if wait_time > 0:
                logger.warning(f"Rate limit reached for {platform}/{endpoint}. Waiting {wait_time:.0f}s...")
                await asyncio.sleep(wait_time)
                # Reset after waiting
                current_state['count'] = 0
                current_state['window_start'] = time.time()
        
        # Increment counter
        current_state['count'] += 1
        self.save_state()
    
    def get_status(self, platform: str, endpoint: str) -> Dict:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with remaining requests, reset time, and percentage used
        """
        if platform not in self.limits or endpoint not in self.limits[platform]:
            return {'remaining': float('inf'), 'reset_time': None, 'percentage_used': 0}
        
        max_requests, window_seconds = self.limits[platform][endpoint]
        current_state = self.state[platform][endpoint]
        
        elapsed = time.time() - current_state['window_start']
        if elapsed >= window_seconds:
            remaining = max_requests
            reset_time = time.time()
        else:
            remaining = max_requests - current_state['count']
            reset_time = current_state['window_start'] + window_seconds
        
        percentage_used = (current_state['count'] / max_requests) * 100
        
        return {
            'remaining': remaining,
            'reset_time': reset_time,
            'percentage_used': percentage_used
        }


# ============================================================================
# BASE API CLIENT
# ============================================================================

class BaseAPIClient(ABC):
    """Base class for social media API clients."""
    
    def __init__(self, credentials: dict, rate_limiter: RateLimiter):
        """
        Initialize API client.
        
        Args:
            credentials: Platform-specific credentials
            rate_limiter: Rate limiter instance
        """
        self.credentials = credentials
        self.rate_limiter = rate_limiter
        self.platform = self.get_platform_name()
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name (twitter, linkedin, etc.)."""
        pass
    
    @abstractmethod
    async def fetch_user_posts(self, username: str, since_id: Optional[str] = None) -> List[Dict]:
        """
        Fetch posts from a user's timeline.
        
        Args:
            username: Username to fetch posts from
            since_id: Only fetch posts after this ID
        
        Returns:
            List of normalized post dictionaries
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate API credentials by making a test request."""
        pass
    
    @abstractmethod
    async def get_user_info(self, username: str) -> Dict:
        """Get user profile information."""
        pass
    
    def extract_urls(self, post_text: str) -> List[str]:
        """Extract URLs from post text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, post_text)
        return urls


# ============================================================================
# MOCK API CLIENTS (for testing without real API keys)
# ============================================================================

class MockTwitterClient(BaseAPIClient):
    """Mock Twitter client for testing."""
    
    def get_platform_name(self) -> str:
        return "twitter"
    
    async def fetch_user_posts(self, username: str, since_id: Optional[str] = None) -> List[Dict]:
        """Return mock Twitter posts."""
        await self.rate_limiter.acquire(self.platform, 'user_timeline')
        
        # Mock posts about wireless technology
        mock_posts = [
            {
                'id': '1234567890',
                'text': 'Exciting news about Wi-Fi 7! New routers hitting the market. https://example.com/wifi7-news',
                'created_at': datetime.now().isoformat(),
                'author': username,
                'urls': ['https://example.com/wifi7-news'],
                'engagement': {'likes': 150, 'retweets': 45, 'replies': 12, 'quotes': 5},
                'raw': {}
            },
            {
                'id': '1234567891',
                'text': 'Just attended #MWC2024 - amazing 5G demos! Check out this article: https://example.com/mwc-5g',
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'author': username,
                'urls': ['https://example.com/mwc-5g'],
                'engagement': {'likes': 230, 'retweets': 67, 'replies': 23, 'quotes': 8},
                'raw': {}
            }
        ]
        
        return mock_posts
    
    async def validate_credentials(self) -> bool:
        """Mock credential validation."""
        return True
    
    async def get_user_info(self, username: str) -> Dict:
        """Return mock user info."""
        return {
            'username': username,
            'display_name': f'{username} (Mock)',
            'follower_count': 5000,
            'verified': False
        }


class MockLinkedInClient(BaseAPIClient):
    """Mock LinkedIn client for testing."""
    
    def get_platform_name(self) -> str:
        return "linkedin"
    
    async def fetch_user_posts(self, username: str, since_id: Optional[str] = None) -> List[Dict]:
        """Return mock LinkedIn posts."""
        await self.rate_limiter.acquire(self.platform, 'profile_posts')
        
        # Mock posts about wireless technology
        mock_posts = [
            {
                'id': str(int(time.time() * 1000)),
                'text': 'Thrilled to announce our new wireless infrastructure project! Read more: https://example.com/wireless-project',
                'created_at': datetime.now().isoformat(),
                'author': username,
                'urls': ['https://example.com/wireless-project'],
                'engagement': {'likes': 89, 'comments': 15, 'shares': 23},
                'raw': {}
            }
        ]
        
        return mock_posts
    
    async def validate_credentials(self) -> bool:
        """Mock credential validation."""
        return True
    
    async def get_user_info(self, username: str) -> Dict:
        """Return mock user info."""
        return {
            'username': username,
            'display_name': f'{username} (Mock)',
            'follower_count': 3000,
            'verified': False
        }


# ============================================================================
# ENHANCED IMAGE SCRAPER
# ============================================================================

class EnhancedImageScraper:
    """Enhanced image scraper with multi-strategy extraction."""
    
    def __init__(self, cache_ttl=86400):
        """
        Initialize enhanced image scraper.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 24 hours)
        """
        self.cache = {}  # URL -> (image_url, metadata, timestamp)
        self.cache_ttl = cache_ttl
        self.session = None
    
    async def init_session(self):
        """Initialize aiohttp session."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def scrape_article_image(self, article_url: str, article_title: str) -> dict:
        """
        Scrape high-quality image from article URL using multiple strategies.
        
        Args:
            article_url: URL of the article
            article_title: Title of the article
        
        Returns:
            Dictionary with image_url, strategy, metadata, and cached status
        """
        await self.init_session()
        
        # Check cache
        if article_url in self.cache:
            cached_data, timestamp = self.cache[article_url]
            if time.time() - timestamp < self.cache_ttl:
                cached_data['cached'] = True
                return cached_data
        
        try:
            # Fetch article HTML
            async with self.session.get(article_url, allow_redirects=True) as response:
                if response.status != 200:
                    return {'image_url': None, 'strategy': 'failed', 'metadata': {}, 'cached': False}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                base_url = str(response.url)
            
            # Try extraction strategies in order
            strategies = [
                ('opengraph', self.extract_opengraph_image),
                ('twitter_card', self.extract_twitter_card_image),
                ('jsonld', self.extract_jsonld_image),
                ('content_analysis', self.analyze_content_images)
            ]
            
            for strategy_name, strategy_func in strategies:
                result = await strategy_func(soup, base_url)
                if result and result.get('image_url'):
                    result['strategy'] = strategy_name
                    result['cached'] = False
                    # Cache the result
                    self.cache[article_url] = (result, time.time())
                    return result
            
            # All strategies failed
            return {'image_url': None, 'strategy': 'all_failed', 'metadata': {}, 'cached': False}
            
        except Exception as e:
            logger.error(f"Error scraping image from {article_url}: {e}")
            return {'image_url': None, 'strategy': 'error', 'metadata': {'error': str(e)}, 'cached': False}
    
    async def extract_opengraph_image(self, soup: BeautifulSoup, article_url: str) -> Optional[dict]:
        """Extract image from Open Graph metadata."""
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = self.make_absolute_url(og_image['content'], article_url)
            metadata = await self.validate_image_quality(image_url)
            if metadata.get('valid'):
                return {'image_url': image_url, 'metadata': metadata}
        return None
    
    async def extract_twitter_card_image(self, soup: BeautifulSoup, article_url: str) -> Optional[dict]:
        """Extract image from Twitter Card metadata."""
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            image_url = self.make_absolute_url(twitter_image['content'], article_url)
            metadata = await self.validate_image_quality(image_url)
            if metadata.get('valid'):
                return {'image_url': image_url, 'metadata': metadata}
        return None
    
    async def extract_jsonld_image(self, soup: BeautifulSoup, article_url: str) -> Optional[dict]:
        """Extract image from JSON-LD structured data."""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'image' in data:
                    image = data['image']
                    if isinstance(image, str):
                        image_url = self.make_absolute_url(image, article_url)
                    elif isinstance(image, dict) and 'url' in image:
                        image_url = self.make_absolute_url(image['url'], article_url)
                    else:
                        continue
                    
                    metadata = await self.validate_image_quality(image_url)
                    if metadata.get('valid'):
                        return {'image_url': image_url, 'metadata': metadata}
            except (json.JSONDecodeError, KeyError):
                continue
        return None
    
    async def analyze_content_images(self, soup: BeautifulSoup, article_url: str) -> Optional[dict]:
        """Analyze all images in article content and score them."""
        # Find article content area
        content_selectors = ['article', '.article-content', '.post-content', 'main', '.content']
        content_area = None
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                break
        
        if not content_area:
            content_area = soup
        
        # Find all images
        images = content_area.find_all('img')
        scored_images = []
        
        for position, img in enumerate(images):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            
            image_url = self.make_absolute_url(src, article_url)
            
            # Skip obvious non-article images
            if any(keyword in image_url.lower() for keyword in ['logo', 'icon', 'avatar', 'pixel', 'tracking']):
                continue
            
            metadata = await self.validate_image_quality(image_url)
            if metadata.get('valid'):
                score = self.score_image(metadata, position, 0.5)  # Default context score
                scored_images.append((score, image_url, metadata))
        
        if scored_images:
            # Return highest scoring image
            scored_images.sort(reverse=True, key=lambda x: x[0])
            best_score, best_url, best_metadata = scored_images[0]
            return {'image_url': best_url, 'metadata': best_metadata}
        
        return None
    
    async def validate_image_quality(self, image_url: str) -> dict:
        """
        Validate image quality and extract metadata.
        
        Returns:
            Dictionary with valid flag, dimensions, file size, and content type
        """
        try:
            # Use HEAD request first to check content type and size
            async with self.session.head(image_url, allow_redirects=True) as response:
                if response.status != 200:
                    return {'valid': False, 'reason': 'not_accessible'}
                
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    return {'valid': False, 'reason': 'not_image'}
                
                content_length = int(response.headers.get('Content-Length', 0))
                if content_length < 10000:  # 10KB minimum
                    return {'valid': False, 'reason': 'too_small'}
            
            # Download image to check dimensions
            async with self.session.get(image_url) as response:
                if response.status != 200:
                    return {'valid': False, 'reason': 'download_failed'}
                
                image_data = await response.read()
                img = Image.open(BytesIO(image_data))
                width, height = img.size
                
                if width < 400 or height < 300:
                    return {'valid': False, 'reason': 'dimensions_too_small'}
                
                return {
                    'valid': True,
                    'width': width,
                    'height': height,
                    'file_size': len(image_data),
                    'content_type': content_type
                }
        
        except Exception as e:
            logger.debug(f"Image validation failed for {image_url}: {e}")
            return {'valid': False, 'reason': 'validation_error', 'error': str(e)}
    
    def score_image(self, metadata: dict, position: int, context_score: float) -> float:
        """
        Calculate quality score for an image.
        
        Args:
            metadata: Image metadata from validation
            position: Position in DOM (0 = first)
            context_score: Relevance to article content (0-1)
        
        Returns:
            Quality score (0-100)
        """
        score = 0.0
        
        # Dimension score (max 30 points)
        width = metadata.get('width', 0)
        height = metadata.get('height', 0)
        if width >= 1200 and height >= 630:
            score += 30
        elif width >= 800 and height >= 600:
            score += 20
        elif width >= 400 and height >= 300:
            score += 10
        
        # File size score (max 20 points)
        file_size = metadata.get('file_size', 0)
        if file_size >= 100000:  # 100KB
            score += 20
        elif file_size >= 50000:  # 50KB
            score += 15
        elif file_size >= 10000:  # 10KB
            score += 10
        
        # Position score (max 15 points)
        if position == 0:
            score += 15
        elif position <= 2:
            score += 10
        elif position <= 5:
            score += 5
        
        # Context score (max 20 points)
        score += context_score * 20
        
        # Aspect ratio score (max 15 points)
        if width > 0 and height > 0:
            ratio = width / height
            if 1.5 <= ratio <= 1.8:  # 16:9
                score += 15
            elif 1.2 <= ratio <= 1.4:  # 4:3
                score += 10
            elif 0.9 <= ratio <= 1.1:  # Square
                score += 5
        
        return score
    
    def make_absolute_url(self, url: str, base_url: str) -> str:
        """Convert relative URL to absolute URL."""
        if url.startswith('http'):
            return url
        return urljoin(base_url, url)



# ============================================================================
# SOCIAL MEDIA MONITOR
# ============================================================================

class SocialMediaMonitor:
    """Monitors configured social media accounts and extracts content."""
    
    def __init__(self, db_path: str, rate_limiter: RateLimiter, wifi_keywords: List[str]):
        """
        Initialize social media monitor.
        
        Args:
            db_path: Path to SQLite database
            rate_limiter: Rate limiter instance
            wifi_keywords: List of wireless technology keywords for filtering
        """
        self.db_path = db_path
        self.rate_limiter = rate_limiter
        self.wifi_keywords = wifi_keywords
        self.clients = {}  # platform -> client instance
    
    def initialize_clients(self):
        """Initialize API clients for all configured platforms."""
        # For now, use mock clients for testing
        # In production, this would load real credentials and create real clients
        self.clients['twitter'] = MockTwitterClient({}, self.rate_limiter)
        self.clients['linkedin'] = MockLinkedInClient({}, self.rate_limiter)
        logger.info("Initialized mock social media clients")
    
    async def fetch_all_accounts(self) -> Dict[str, int]:
        """
        Fetch posts from all active monitored accounts.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'accounts_fetched': 0,
            'posts_fetched': 0,
            'articles_discovered': 0,
            'errors': 0
        }
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all active accounts
        cursor.execute("""
            SELECT id, platform, username, last_post_id
            FROM social_accounts
            WHERE active = 1
        """)
        
        accounts = cursor.fetchall()
        
        for account in accounts:
            account_id = account['id']
            platform = account['platform']
            username = account['username']
            last_post_id = account['last_post_id']
            
            try:
                if platform not in self.clients:
                    logger.warning(f"No client for platform: {platform}")
                    continue
                
                client = self.clients[platform]
                posts = await client.fetch_user_posts(username, since_id=last_post_id)
                
                for post in posts:
                    # Filter by relevance
                    if not self.is_relevant_post(post['text']):
                        continue
                    
                    # Store post
                    post_db_id = self.store_post(conn, account_id, post)
                    stats['posts_fetched'] += 1
                    
                    # Extract and process article URLs
                    for url in post['urls']:
                        if self.is_article_url(url):
                            article_id = await self.process_article_url(conn, url, post_db_id, account_id)
                            if article_id:
                                stats['articles_discovered'] += 1
                
                # Update last_post_id
                if posts:
                    latest_post_id = posts[0]['id']
                    cursor.execute("""
                        UPDATE social_accounts
                        SET last_post_id = ?, last_fetched = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (latest_post_id, account_id))
                
                stats['accounts_fetched'] += 1
                
            except Exception as e:
                logger.error(f"Error fetching {username} on {platform}: {e}")
                stats['errors'] += 1
        
        conn.commit()
        conn.close()
        
        return stats
    
    def is_relevant_post(self, text: str) -> bool:
        """Check if post is relevant to wireless technology."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.wifi_keywords)
    
    def store_post(self, conn: sqlite3.Connection, account_id: int, post: dict) -> int:
        """Store social media post in database."""
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO social_posts
                (account_id, post_id, text, created_at, engagement_likes, 
                 engagement_shares, engagement_comments, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id,
                post['id'],
                post['text'],
                post['created_at'],
                post['engagement'].get('likes', 0),
                post['engagement'].get('shares', 0) + post['engagement'].get('retweets', 0),
                post['engagement'].get('comments', 0) + post['engagement'].get('replies', 0),
                json.dumps(post['raw'])
            ))
            
            post_db_id = cursor.lastrowid
            return post_db_id
        except sqlite3.IntegrityError:
            # Post already exists
            cursor.execute("""
                SELECT id FROM social_posts
                WHERE account_id = ? AND post_id = ?
            """, (account_id, post['id']))
            result = cursor.fetchone()
            return result[0] if result else None
    
    async def process_article_url(self, conn: sqlite3.Connection, url: str, post_id: int, account_id: int) -> Optional[int]:
        """
        Process an article URL from a social media post.
        
        Returns:
            Article ID if successfully processed, None otherwise
        """
        cursor = conn.cursor()
        
        # Check if article already exists
        cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
        existing = cursor.fetchone()
        
        if existing:
            article_id = existing[0]
            # Update social metadata
            cursor.execute("""
                UPDATE articles
                SET social_source = 1,
                    share_count = share_count + 1
                WHERE id = ?
            """, (article_id,))
        else:
            # Would fetch article content here
            # For now, just create a placeholder
            article_id = None
        
        # Link article to social post
        if article_id:
            try:
                cursor.execute("""
                    INSERT INTO social_article_shares
                    (article_id, post_id, account_id)
                    VALUES (?, ?, ?)
                """, (article_id, post_id, account_id))
            except sqlite3.IntegrityError:
                pass  # Already linked
        
        return article_id
    
    def is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article (not social media, images, etc.)."""
        excluded_domains = ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com',
                           'instagram.com', 'youtube.com', 'youtu.be']
        excluded_extensions = ['.jpg', '.png', '.gif', '.mp4', '.pdf']
        
        url_lower = url.lower()
        
        for domain in excluded_domains:
            if domain in url_lower:
                return False
        
        for ext in excluded_extensions:
            if url_lower.endswith(ext):
                return False
        
        return True


# ============================================================================
# WILD WI-FI CURATOR
# ============================================================================

class WildWiFiCurator:
    """Curates Wild Wi-Fi stories with automatic scoring and featuring."""
    
    def __init__(self, db_path: str):
        """
        Initialize curator.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.humor_indicators = [
            'unexpected', 'ironically', 'surprisingly', 'accidentally',
            'somehow', 'turns out', 'believe it or not', 'absurd',
            'ridiculous', 'hilarious', 'bizarre', 'strange', 'weird',
            'funny', 'amusing', 'comical'
        ]
        self.tech_keywords = [
            'wifi', 'wi-fi', 'wireless', 'router', 'signal', 'network',
            'internet', 'connection', 'bandwidth', 'ssid', 'password',
            '5g', 'cellular', 'antenna', 'modem'
        ]
    
    def calculate_humor_score(self, story_text: str) -> float:
        """
        Calculate humor score for a story.
        
        Args:
            story_text: Story text content
        
        Returns:
            Humor score (0-10)
        """
        score = 0.0
        text_lower = story_text.lower()
        
        # Humor indicators (max 3 points)
        indicator_count = sum(1 for indicator in self.humor_indicators if indicator in text_lower)
        score += min(indicator_count * 1.0, 3.0)
        
        # Length bonus for detailed stories (max 2 points)
        word_count = len(story_text.split())
        if 100 <= word_count <= 500:
            score += 2.0
        elif word_count > 50:
            score += 1.0
        
        # Specific details bonus (max 2 points)
        has_location = bool(re.search(r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b', story_text))
        has_numbers = bool(re.search(r'\d+', story_text))
        if has_location:
            score += 1.0
        if has_numbers:
            score += 1.0
        
        # Irony/contrast bonus (max 3 points)
        irony_patterns = ['but', 'however', 'instead', 'actually', 'turns out']
        irony_count = sum(1 for pattern in irony_patterns if pattern in text_lower)
        score += min(irony_count * 1.0, 3.0)
        
        return min(score, 10.0)
    
    def calculate_tech_relevance_score(self, story_text: str, tech_relevance: str) -> float:
        """
        Calculate technical relevance score.
        
        Args:
            story_text: Story text content
            tech_relevance: Technical relevance explanation
        
        Returns:
            Tech relevance score (0-10)
        """
        score = 0.0
        text_lower = (story_text + ' ' + (tech_relevance or '')).lower()
        
        # Tech keyword count (max 6 points)
        keyword_count = sum(1 for keyword in self.tech_keywords if keyword in text_lower)
        score += min(keyword_count * 0.5, 6.0)
        
        # Tech relevance explanation quality (max 4 points)
        if tech_relevance:
            relevance_length = len(tech_relevance.split())
            if relevance_length >= 20:
                score += 4.0
            elif relevance_length >= 10:
                score += 2.0
            elif relevance_length >= 5:
                score += 1.0
        
        return min(score, 10.0)
    
    def calculate_quality_score(self, story: dict) -> float:
        """
        Calculate overall quality score for a story.
        
        Args:
            story: Story dictionary with all fields
        
        Returns:
            Quality score (0-100)
        """
        # Calculate component scores
        humor_score = self.calculate_humor_score(story['story'])
        tech_score = self.calculate_tech_relevance_score(story['story'], story.get('tech_relevance', ''))
        
        # Completeness score (0-10)
        completeness = 0.0
        if story.get('location'):
            completeness += 3.0
        if story.get('source_url'):
            completeness += 3.0
        if story.get('category'):
            completeness += 2.0
        if story.get('tech_relevance'):
            completeness += 2.0
        
        # Length score (0-10)
        word_count = len(story['story'].split())
        if 100 <= word_count <= 500:
            length_score = 10.0
        elif 50 <= word_count < 100:
            length_score = 7.0
        elif word_count >= 500:
            length_score = 5.0
        else:
            length_score = 3.0
        
        # Weighted combination
        quality_score = (
            humor_score * 0.4 +
            tech_score * 0.3 +
            completeness * 0.2 +
            length_score * 0.1
        ) * 10  # Scale to 0-100
        
        return min(quality_score, 100.0)
    
    def update_all_scores(self):
        """Recalculate scores for all stories."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM wild_wifi_stories")
        stories = cursor.fetchall()
        
        for story in stories:
            story_dict = dict(story)
            quality_score = self.calculate_quality_score(story_dict)
            humor_score = self.calculate_humor_score(story_dict['story'])
            
            cursor.execute("""
                UPDATE wild_wifi_stories
                SET quality_score = ?, humor_rating = ?
                WHERE id = ?
            """, (quality_score, int(humor_score), story_dict['id']))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated scores for {len(stories)} Wild Wi-Fi stories")
    
    def update_featured_stories(self):
        """Update which stories are featured based on quality scores."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all stories sorted by quality with freshness boost
        cursor.execute("""
            SELECT id, quality_score, created_at
            FROM wild_wifi_stories
            WHERE approved = 1
            ORDER BY quality_score DESC
        """)
        stories = cursor.fetchall()
        
        # Apply freshness boost
        now = datetime.now()
        scored_stories = []
        for story in stories:
            created_at = datetime.fromisoformat(story['created_at'])
            age_days = (now - created_at).days
            
            # Boost recent stories
            freshness_boost = 0
            if age_days < 7:
                freshness_boost = 10
            elif age_days < 30:
                freshness_boost = 5
            
            adjusted_score = story['quality_score'] + freshness_boost
            scored_stories.append((story['id'], adjusted_score))
        
        # Sort by adjusted score
        scored_stories.sort(key=lambda x: x[1], reverse=True)
        
        # Feature top 5 stories with quality > 75
        featured_ids = []
        for story_id, score in scored_stories[:5]:
            if score >= 75:
                featured_ids.append(story_id)
        
        # Update featured status
        cursor.execute("UPDATE wild_wifi_stories SET featured = 0")
        if featured_ids:
            placeholders = ','.join('?' * len(featured_ids))
            cursor.execute(f"UPDATE wild_wifi_stories SET featured = 1 WHERE id IN ({placeholders})", featured_ids)
        
        conn.commit()
        conn.close()
        logger.info(f"Featured {len(featured_ids)} Wild Wi-Fi stories")


# ============================================================================
# SOCIAL EVENT DISCOVERER
# ============================================================================

class SocialEventDiscoverer:
    """Discovers industry events from social media posts."""
    
    def __init__(self, db_path: str):
        """
        Initialize event discoverer.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.event_patterns = [
            r'\b(CES|MWC|IFA|NRF|CTIA|5G Summit|Wi-Fi World Congress)\s*(\d{4})?\b',
            r'\b(\w+\s+Conference|Summit|Expo|Show)\s*(\d{4})?\b',
            r'\#(\w+\d{4})\b'  # Hashtags like #CES2024
        ]
        self.known_events = {
            'CES': {'month': 1, 'day': 5, 'duration': 4},
            'MWC': {'month': 2, 'day': 26, 'duration': 4},
            'IFA': {'month': 9, 'day': 6, 'duration': 5},
            'NRF': {'month': 1, 'day': 14, 'duration': 3}
        }
    
    def extract_events_from_text(self, text: str) -> List[Dict]:
        """Extract event mentions from text."""
        events = []
        
        for pattern in self.event_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                event_name = match.group(1)
                year = match.group(2) if len(match.groups()) > 1 else None
                
                if not year:
                    year = str(datetime.now().year)
                
                events.append({
                    'name': event_name,
                    'year': int(year),
                    'text': match.group(0)
                })
        
        return events
    
    def calculate_event_confidence(self, event: dict, post_text: str) -> float:
        """Calculate confidence score for discovered event."""
        score = 0.0
        
        # Known event name (40 points)
        if any(known in event['name'].upper() for known in self.known_events.keys()):
            score += 40.0
        
        # Location mention (20 points)
        if re.search(r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b', post_text):
            score += 20.0
        
        # Hashtags (15 points)
        if '#' in post_text:
            score += 15.0
        
        # Date mention (15 points)
        if re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\b', post_text):
            score += 15.0
        
        # Attendance keywords (10 points)
        attendance_keywords = ['attending', 'going to', 'see you at', 'excited for', 'can\'t wait']
        if any(keyword in post_text.lower() for keyword in attendance_keywords):
            score += 10.0
        
        return min(score, 100.0)
    
    async def discover_events_from_posts(self) -> int:
        """Discover events from recent social media posts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get recent posts (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute("""
            SELECT id, account_id, text, created_at
            FROM social_posts
            WHERE created_at >= ?
        """, (thirty_days_ago,))
        
        posts = cursor.fetchall()
        events_discovered = 0
        
        for post in posts:
            events = self.extract_events_from_text(post['text'])
            
            for event in events:
                confidence = self.calculate_event_confidence(event, post['text'])
                
                # Check if event already exists
                cursor.execute("""
                    SELECT id FROM industry_events
                    WHERE name LIKE ? AND start_date LIKE ?
                """, (f"%{event['name']}%", f"{event['year']}%"))
                
                existing = cursor.fetchone()
                
                if existing:
                    event_id = existing['id']
                    # Update confidence and mention count
                    cursor.execute("""
                        UPDATE industry_events
                        SET confidence_score = MAX(confidence_score, ?),
                            social_mention_count = social_mention_count + 1
                        WHERE id = ?
                    """, (confidence, event_id))
                else:
                    # Create new event
                    dates = self.estimate_event_dates(event['name'], event['year'])
                    cursor.execute("""
                        INSERT INTO industry_events
                        (name, start_date, end_date, confidence_score, discovered_from_social, social_mention_count)
                        VALUES (?, ?, ?, ?, 1, 1)
                    """, (f"{event['name']} {event['year']}", dates['start'], dates['end'], confidence))
                    event_id = cursor.lastrowid
                    events_discovered += 1
                
                # Link post to event
                try:
                    cursor.execute("""
                        INSERT INTO event_social_mentions
                        (event_id, post_id, account_id)
                        VALUES (?, ?, ?)
                    """, (event_id, post['id'], post['account_id']))
                except sqlite3.IntegrityError:
                    pass  # Already linked
        
        conn.commit()
        conn.close()
        logger.info(f"Discovered {events_discovered} new events from social media")
        return events_discovered
    
    def estimate_event_dates(self, event_name: str, year: int) -> dict:
        """Estimate event dates based on known schedules."""
        event_upper = event_name.upper()
        
        for known_event, schedule in self.known_events.items():
            if known_event in event_upper:
                start_date = datetime(year, schedule['month'], schedule['day'])
                end_date = start_date + timedelta(days=schedule['duration'])
                return {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
        
        # Default to current date ± 3 days
        now = datetime.now()
        return {
            'start': now.strftime('%Y-%m-%d'),
            'end': (now + timedelta(days=3)).strftime('%Y-%m-%d')
        }
