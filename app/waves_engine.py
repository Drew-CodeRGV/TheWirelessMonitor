"""
Waves: The Wireless Podcast - News Engine
Comprehensive news analysis and trend tracking for the wireless industry
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class WavesEngine:
    """Main engine for Waves podcast news analysis"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize Waves database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main stories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                content TEXT,
                snippet TEXT,
                source TEXT NOT NULL,
                source_type TEXT NOT NULL,
                category TEXT,
                published_date TIMESTAMP,
                fetched_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Scoring
                cross_source_count INTEGER DEFAULT 1,
                engagement_score REAL DEFAULT 0,
                total_score REAL DEFAULT 0,
                
                -- Analysis
                synopsis TEXT,
                deep_dive TEXT,
                crossover_connection TEXT,
                crossover_direction TEXT,
                
                -- Metadata
                author TEXT,
                tags TEXT,
                read_status INTEGER DEFAULT 0,
                in_cutsheet INTEGER DEFAULT 0,
                relevancy_feedback INTEGER DEFAULT 0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Story scores tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_story_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                score_type TEXT NOT NULL,
                score_value REAL NOT NULL,
                source TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES waves_stories(id)
            )
        ''')
        
        # Weekly and monthly themes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period_type TEXT NOT NULL,
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                theme_title TEXT NOT NULL,
                theme_description TEXT,
                key_stories TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(period_type, period_start)
            )
        ''')
        
        # Ongoing industry conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_name TEXT UNIQUE NOT NULL,
                description TEXT,
                related_stories TEXT,
                first_seen DATE,
                last_updated DATE,
                story_count INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Tech crossover connections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_crossovers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                crossover_type TEXT NOT NULL,
                direction TEXT NOT NULL,
                tech_area TEXT NOT NULL,
                connection_description TEXT,
                impact_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES waves_stories(id)
            )
        ''')
        
        # Podcast cutsheet
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_cutsheet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                segment TEXT,
                notes TEXT,
                order_position INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES waves_stories(id)
            )
        ''')
        
        # User feedback for learning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                story_id INTEGER NOT NULL,
                feedback_type TEXT NOT NULL,
                feedback_value INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES waves_stories(id)
            )
        ''')
        
        # Story clusters for trend analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_story_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_name TEXT NOT NULL,
                cluster_description TEXT,
                story_ids TEXT NOT NULL,
                period_start DATE,
                period_end DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Source monitoring configuration
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waves_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_url TEXT,
                enabled INTEGER DEFAULT 1,
                last_checked TIMESTAMP,
                check_frequency_minutes INTEGER DEFAULT 60,
                config_json TEXT
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_waves_stories_date ON waves_stories(published_date DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_waves_stories_score ON waves_stories(total_score DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_waves_stories_category ON waves_stories(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_waves_stories_cutsheet ON waves_stories(in_cutsheet)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_waves_crossovers_story ON waves_crossovers(story_id)')
        
        conn.commit()
        conn.close()
        
        logger.info("Waves database initialized successfully")
    
    def add_story(self, story_data: Dict) -> Optional[int]:
        """
        Add a new story to the database
        
        Args:
            story_data: Dictionary with story information
            
        Returns:
            Story ID if successful, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check for duplicates by URL
            existing = cursor.execute(
                'SELECT id FROM waves_stories WHERE url = ?',
                (story_data['url'],)
            ).fetchone()
            
            if existing:
                logger.debug(f"Story already exists: {story_data['url']}")
                return existing[0]
            
            # Check for similar titles (prevent duplicates with different URLs)
            similar = self._find_similar_story(cursor, story_data['title'])
            if similar:
                logger.info(f"Similar story found, skipping: {story_data['title']}")
                return None
            
            # Insert new story
            cursor.execute('''
                INSERT INTO waves_stories (
                    title, url, content, snippet, source, source_type,
                    category, published_date, author, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                story_data.get('title'),
                story_data.get('url'),
                story_data.get('content'),
                story_data.get('snippet'),
                story_data.get('source'),
                story_data.get('source_type'),
                story_data.get('category'),
                story_data.get('published_date'),
                story_data.get('author'),
                json.dumps(story_data.get('tags', []))
            ))
            
            story_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Added new story: {story_data['title']} (ID: {story_id})")
            return story_id
            
        except Exception as e:
            logger.error(f"Error adding story: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def _find_similar_story(self, cursor, title: str, threshold: float = 0.85) -> Optional[int]:
        """Find stories with similar titles"""
        recent_stories = cursor.execute('''
            SELECT id, title FROM waves_stories
            WHERE published_date >= date('now', '-7 days')
            ORDER BY published_date DESC
            LIMIT 100
        ''').fetchall()
        
        for story_id, existing_title in recent_stories:
            similarity = SequenceMatcher(None, title.lower(), existing_title.lower()).ratio()
            if similarity >= threshold:
                return story_id
        
        return None
    
    def calculate_story_score(self, story_id: int) -> float:
        """
        Calculate total score for a story based on:
        - Cross-source frequency
        - Engagement signals
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get story data
            story = cursor.execute(
                'SELECT cross_source_count, engagement_score FROM waves_stories WHERE id = ?',
                (story_id,)
            ).fetchone()
            
            if not story:
                return 0.0
            
            cross_source_count, engagement_score = story
            
            # Scoring formula:
            # - Cross-source frequency: 10 points per source
            # - Engagement: normalized 0-100
            frequency_score = min(cross_source_count * 10, 50)  # Cap at 50
            engagement_normalized = min(engagement_score, 50)  # Cap at 50
            
            total_score = frequency_score + engagement_normalized
            
            # Update story score
            cursor.execute('''
                UPDATE waves_stories 
                SET total_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (total_score, story_id))
            
            # Record score calculation
            cursor.execute('''
                INSERT INTO waves_story_scores (story_id, score_type, score_value)
                VALUES (?, 'total', ?)
            ''', (story_id, total_score))
            
            conn.commit()
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating story score: {e}")
            return 0.0
        finally:
            conn.close()
    
    def categorize_story(self, story_data: Dict) -> str:
        """
        Categorize story into: What's New, What's Now, What's Next, News of the Weird
        """
        title = story_data.get('title', '').lower()
        content = story_data.get('content', '').lower()
        snippet = story_data.get('snippet', '').lower()
        text = f"{title} {content} {snippet}"
        
        # What's New: M&A, acquisitions, product launches, breaking news
        new_keywords = [
            'acquisition', 'merger', 'acquires', 'launches', 'announces',
            'unveils', 'introduces', 'releases', 'breaking', 'just announced'
        ]
        
        # What's Now: trending, discussions, current debates
        now_keywords = [
            'trending', 'debate', 'discussion', 'controversy', 'viral',
            'everyone is talking', 'hot topic', 'industry buzz'
        ]
        
        # What's Next: future tech, standards, regulatory pipeline
        next_keywords = [
            'wifi 7', 'wifi7', '6g', 'future', 'upcoming', 'roadmap',
            'next generation', 'emerging', 'spectrum auction', 'regulatory',
            'standards', 'draft', 'proposal'
        ]
        
        # News of the Weird: quirky, unusual, creative applications
        weird_keywords = [
            'unusual', 'bizarre', 'weird', 'quirky', 'creative', 'unexpected',
            'surprising', 'odd', 'strange', 'hilarious', 'funny'
        ]
        
        # Score each category
        scores = {
            "What's New": sum(1 for kw in new_keywords if kw in text),
            "What's Now": sum(1 for kw in now_keywords if kw in text),
            "What's Next": sum(1 for kw in next_keywords if kw in text),
            "News of the Weird": sum(1 for kw in weird_keywords if kw in text)
        }
        
        # Return category with highest score, default to What's Now
        if max(scores.values()) == 0:
            return "What's Now"
        
        return max(scores, key=scores.get)
    
    def add_to_cutsheet(self, story_id: int, segment: str, notes: str = "") -> bool:
        """Add story to podcast cutsheet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current max position
            max_pos = cursor.execute(
                'SELECT MAX(order_position) FROM waves_cutsheet'
            ).fetchone()[0] or 0
            
            # Add to cutsheet
            cursor.execute('''
                INSERT INTO waves_cutsheet (story_id, segment, notes, order_position)
                VALUES (?, ?, ?, ?)
            ''', (story_id, segment, notes, max_pos + 1))
            
            # Mark story as in cutsheet
            cursor.execute('''
                UPDATE waves_stories SET in_cutsheet = 1 WHERE id = ?
            ''', (story_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error adding to cutsheet: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_stories(self, 
                   days: int = 7,
                   category: Optional[str] = None,
                   min_score: float = 0,
                   limit: int = 100) -> List[Dict]:
        """Get stories with filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM waves_stories
            WHERE published_date >= date('now', '-{} days')
            AND total_score >= ?
        '''.format(days)
        
        params = [min_score]
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        query += ' ORDER BY total_score DESC, published_date DESC LIMIT ?'
        params.append(limit)
        
        stories = cursor.execute(query, params).fetchall()
        conn.close()
        
        return [dict(story) for story in stories]
    
    def get_cutsheet(self) -> List[Dict]:
        """Get all stories in the cutsheet"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        stories = cursor.execute('''
            SELECT 
                c.id as cutsheet_id,
                c.segment,
                c.notes,
                c.order_position,
                s.*
            FROM waves_cutsheet c
            JOIN waves_stories s ON c.story_id = s.id
            ORDER BY c.order_position
        ''').fetchall()
        
        conn.close()
        return [dict(story) for story in stories]


class WavesAnalyzer:
    """Analysis engine for trend detection and synthesis"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def cluster_stories(self, stories: List[Dict]) -> List[Dict]:
        """
        Group stories into thematic clusters
        
        Returns list of clusters with:
        - cluster_name
        - cluster_description
        - story_ids
        - story_count
        """
        # Simple keyword-based clustering
        # TODO: Enhance with ML-based clustering
        
        clusters = {}
        
        for story in stories:
            # Extract key themes from title and content
            themes = self._extract_themes(story)
            
            for theme in themes:
                if theme not in clusters:
                    clusters[theme] = []
                clusters[theme].append(story['id'])
        
        # Convert to list format
        result = []
        for theme, story_ids in clusters.items():
            if len(story_ids) >= 2:  # Only clusters with 2+ stories
                result.append({
                    'cluster_name': theme,
                    'story_ids': story_ids,
                    'story_count': len(story_ids)
                })
        
        return sorted(result, key=lambda x: x['story_count'], reverse=True)
    
    def _extract_themes(self, story: Dict) -> List[str]:
        """Extract key themes from story"""
        text = f"{story.get('title', '')} {story.get('snippet', '')}".lower()
        
        themes = []
        
        # Technology themes
        tech_patterns = {
            'WiFi 7': r'wifi\s*7|wi-fi\s*7',
            '5G': r'\b5g\b',
            '6G': r'\b6g\b',
            'Spectrum': r'spectrum|frequency|band',
            'Security': r'security|breach|hack|vulnerability',
            'IoT': r'\biot\b|internet of things|smart home',
            'Enterprise': r'enterprise|business|corporate',
            'Standards': r'standard|ieee|alliance',
            'Infrastructure': r'infrastructure|deployment|rollout',
            'AI/ML': r'\bai\b|machine learning|artificial intelligence'
        }
        
        for theme, pattern in tech_patterns.items():
            if re.search(pattern, text):
                themes.append(theme)
        
        return themes if themes else ['General Wireless']
    
    def identify_weekly_theme(self, stories: List[Dict]) -> Dict:
        """
        Identify the dominant theme for the week
        
        Returns:
        - theme_title
        - theme_description
        - key_stories (list of story IDs)
        """
        if not stories:
            return {
                'theme_title': 'No significant theme',
                'theme_description': 'Insufficient stories this week',
                'key_stories': []
            }
        
        # Cluster stories
        clusters = self.cluster_stories(stories)
        
        if not clusters:
            return {
                'theme_title': 'Diverse wireless developments',
                'theme_description': 'This week saw various developments across the wireless industry',
                'key_stories': [s['id'] for s in stories[:3]]
            }
        
        # Get largest cluster as dominant theme
        dominant = clusters[0]
        
        return {
            'theme_title': dominant['cluster_name'],
            'theme_description': f"This week, the industry was focused on {dominant['cluster_name']} with {dominant['story_count']} related stories",
            'key_stories': dominant['story_ids'][:5]
        }


class WavesSourceMonitor:
    """Monitor various news sources for wireless industry content"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = WavesEngine(db_path)
    
    def fetch_from_rss(self, feed_url: str, source_name: str) -> int:
        """Fetch stories from RSS feed"""
        import feedparser
        
        try:
            feed = feedparser.parse(feed_url)
            stories_added = 0
            
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                story_data = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'snippet': entry.get('summary', '')[:500],
                    'content': entry.get('description', ''),
                    'source': source_name,
                    'source_type': 'rss',
                    'published_date': entry.get('published', datetime.now().isoformat()),
                    'author': entry.get('author', ''),
                    'tags': [tag.get('term', '') for tag in entry.get('tags', [])]
                }
                
                # Categorize
                story_data['category'] = self.engine.categorize_story(story_data)
                
                # Add to database
                story_id = self.engine.add_story(story_data)
                if story_id:
                    stories_added += 1
                    # Calculate initial score
                    self.engine.calculate_story_score(story_id)
            
            return stories_added
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return 0
    
    def search_news(self, query: str, source_name: str = "Web Search") -> int:
        """Search for news using DuckDuckGo"""
        import requests
        
        try:
            # Use DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query + ' news')}&format=json&no_html=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return 0
            
            data = response.json()
            stories_added = 0
            
            # Extract related topics
            if 'RelatedTopics' in data:
                for topic in data['RelatedTopics'][:10]:
                    if isinstance(topic, dict) and 'Text' in topic and 'FirstURL' in topic:
                        story_data = {
                            'title': topic.get('Text', '')[:200],
                            'url': topic.get('FirstURL', ''),
                            'snippet': topic.get('Text', ''),
                            'content': '',
                            'source': source_name,
                            'source_type': 'web_search',
                            'published_date': datetime.now().isoformat(),
                            'tags': [query]
                        }
                        
                        story_data['category'] = self.engine.categorize_story(story_data)
                        
                        story_id = self.engine.add_story(story_data)
                        if story_id:
                            stories_added += 1
                            self.engine.calculate_story_score(story_id)
            
            return stories_added
            
        except Exception as e:
            logger.error(f"Error searching news for '{query}': {e}")
            return 0



class WavesSocialMonitor:
    """Monitor X (Twitter) and LinkedIn for wireless industry content"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = WavesEngine(db_path)
    
    async def fetch_x_posts(self, limit: int = 50) -> int:
        """Fetch posts from X (Twitter)"""
        try:
            from x_timeline import XTimelineManager
            
            x_manager = XTimelineManager()
            
            # Get following timeline
            posts = await x_manager.get_following_timeline(limit=limit)
            
            stories_added = 0
            for post in posts:
                # Only add tech-related posts
                if not x_manager.is_tech_related(post.get('text', '')):
                    continue
                
                # Extract URLs from post
                urls = x_manager.extract_urls_from_text(post.get('text', ''))
                primary_url = urls[0] if urls else f"https://twitter.com/i/status/{post.get('id', '')}"
                
                story_data = {
                    'title': post.get('text', '')[:200],
                    'url': primary_url,
                    'snippet': post.get('text', ''),
                    'content': post.get('text', ''),
                    'source': f"X (@{post.get('author', {}).get('username', 'unknown')})",
                    'source_type': 'x_twitter',
                    'published_date': post.get('created_at', datetime.now().isoformat()),
                    'author': post.get('author', {}).get('name', ''),
                    'tags': ['x', 'twitter', 'social']
                }
                
                # Calculate engagement score
                engagement = (
                    post.get('metrics', {}).get('like_count', 0) +
                    post.get('metrics', {}).get('retweet_count', 0) * 2 +
                    post.get('metrics', {}).get('reply_count', 0)
                )
                
                # Categorize
                story_data['category'] = self.engine.categorize_story(story_data)
                
                # Add to database
                story_id = self.engine.add_story(story_data)
                if story_id:
                    # Update engagement score
                    conn = sqlite3.connect(self.db_path)
                    conn.execute('''
                        UPDATE waves_stories 
                        SET engagement_score = ?
                        WHERE id = ?
                    ''', (engagement, story_id))
                    conn.commit()
                    conn.close()
                    
                    # Calculate total score
                    self.engine.calculate_story_score(story_id)
                    stories_added += 1
            
            return stories_added
            
        except Exception as e:
            logger.error(f"Error fetching X posts: {e}")
            return 0
    
    def fetch_linkedin_posts(self, limit: int = 50) -> int:
        """Fetch posts from LinkedIn (mock for now)"""
        try:
            # Mock LinkedIn posts for now
            # TODO: Implement real LinkedIn API integration
            
            mock_posts = [
                {
                    'title': 'WiFi 7 deployment accelerates in enterprise',
                    'text': 'Major enterprises are accelerating WiFi 7 deployments, citing improved performance and capacity.',
                    'author': 'Cisco',
                    'url': 'https://linkedin.com/posts/cisco-wifi7',
                    'engagement': 150
                },
                {
                    'title': '5G private networks gaining traction',
                    'text': 'Private 5G networks are becoming the preferred choice for industrial IoT applications.',
                    'author': 'Ericsson',
                    'url': 'https://linkedin.com/posts/ericsson-5g',
                    'engagement': 200
                },
                {
                    'title': 'Spectrum auction results announced',
                    'text': 'FCC announces results of latest spectrum auction, with major carriers securing key bands.',
                    'author': 'FCC',
                    'url': 'https://linkedin.com/posts/fcc-spectrum',
                    'engagement': 300
                }
            ]
            
            stories_added = 0
            for post in mock_posts[:limit]:
                story_data = {
                    'title': post['title'],
                    'url': post['url'],
                    'snippet': post['text'],
                    'content': post['text'],
                    'source': f"LinkedIn ({post['author']})",
                    'source_type': 'linkedin',
                    'published_date': datetime.now().isoformat(),
                    'author': post['author'],
                    'tags': ['linkedin', 'social']
                }
                
                story_data['category'] = self.engine.categorize_story(story_data)
                
                story_id = self.engine.add_story(story_data)
                if story_id:
                    # Update engagement score
                    conn = sqlite3.connect(self.db_path)
                    conn.execute('''
                        UPDATE waves_stories 
                        SET engagement_score = ?
                        WHERE id = ?
                    ''', (post['engagement'], story_id))
                    conn.commit()
                    conn.close()
                    
                    self.engine.calculate_story_score(story_id)
                    stories_added += 1
            
            return stories_added
            
        except Exception as e:
            logger.error(f"Error fetching LinkedIn posts: {e}")
            return 0
    
    async def fetch_all_social(self) -> Dict[str, int]:
        """Fetch from all social sources"""
        results = {
            'x': 0,
            'linkedin': 0
        }
        
        # Fetch X posts
        results['x'] = await self.fetch_x_posts()
        
        # Fetch LinkedIn posts
        results['linkedin'] = self.fetch_linkedin_posts()
        
        return results
