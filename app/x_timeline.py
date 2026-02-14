"""
X (Twitter) Timeline Integration
Fetches top stories from following and followers
"""
import os
import json
import logging
from typing import List, Dict, Optional
import re
from collections import Counter
from dotenv import load_dotenv
import tweepy

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class XTimelineManager:
    """Manages X timeline integration for fetching top stories"""
    
    def __init__(self):
        self.use_mock = True  # Default to mock mode
        self.client = None
        self.config = self._load_config()
        
        # Try to initialize real X API client if credentials exist
        try:
            api_key = os.getenv('X_API_KEY')
            api_secret = os.getenv('X_API_SECRET')
            bearer_token = os.getenv('X_BEARER_TOKEN')
            
            if bearer_token:
                # Use Bearer Token authentication (simpler, read-only)
                self.client = tweepy.Client(bearer_token=bearer_token)
                self.use_mock = False
                logger.info("X API credentials found - using real API with Bearer Token")
            elif api_key and api_secret:
                # Fallback to OAuth 1.0a if no bearer token
                auth = tweepy.OAuth1UserHandler(api_key, api_secret)
                api = tweepy.API(auth)
                self.client = api
                self.use_mock = False
                logger.info("X API credentials found - using real API with OAuth")
            else:
                logger.info("No X API credentials - using mock data")
        except Exception as e:
            logger.warning(f"Error initializing X API: {e}")
            self.use_mock = True
    
    def _load_config(self) -> Dict:
        """Load account configuration from x_accounts_config.json"""
        try:
            config_path = 'x_accounts_config.json'
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found: {config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if file not found"""
        return {
            "following_accounts": [
                "TechCrunch", "WIRED", "TheVerge", "engadget", "arstechnica"
            ],
            "followers_accounts": [
                "5GTechnologyWorld", "WirelessWeek", "MobileWorldLive"
            ]
        }
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from tweet text"""
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        # Filter out twitter/x.com URLs
        return [url for url in urls if 'twitter.com' not in url and 'x.com' not in url]
    
    def is_tech_related(self, text: str) -> bool:
        """Check if tweet is tech/wireless related"""
        keywords = [
            'wifi', 'wireless', '5g', '6g', 'network', 'connectivity',
            'tech', 'technology', 'ai', 'ml', 'iot', 'cloud',
            'software', 'hardware', 'mobile', 'broadband', 'spectrum'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def score_tweet(self, tweet: Dict) -> float:
        """Score tweet based on engagement and relevance"""
        score = 0.0
        
        # Engagement score (max 50 points)
        likes = tweet.get('likes', 0)
        retweets = tweet.get('retweets', 0)
        replies = tweet.get('replies', 0)
        
        score += min(likes / 100, 20)  # Max 20 points from likes
        score += min(retweets / 20, 20)  # Max 20 points from retweets
        score += min(replies / 10, 10)  # Max 10 points from replies
        
        # URL presence (20 points)
        if self.extract_urls_from_text(tweet.get('text', '')):
            score += 20
        
        # Tech relevance (30 points)
        if self.is_tech_related(tweet.get('text', '')):
            score += 30
        
        return score
    
    async def get_following_timeline(self, limit: int = 50) -> List[Dict]:
        """Get recent tweets from accounts you follow"""
        if self.use_mock:
            return self._get_mock_following_timeline(limit)
        
        try:
            logger.info("Using app-only auth - fetching from public tech accounts")
            
            # Get accounts from config
            public_accounts = self.config.get('following_accounts', [])[:10]  # Limit to 10 to avoid rate limits
            
            all_tweets = []
            
            # Fetch recent tweets from each public account
            for username in public_accounts[:5]:  # Process 5 at a time
                try:
                    user = self.client.get_user(username=username)
                    if not user.data:
                        continue
                    
                    tweets = self.client.get_users_tweets(
                        id=user.data.id,
                        max_results=10,
                        tweet_fields=['created_at', 'public_metrics'],
                        exclude=['retweets', 'replies']
                    )
                    
                    if tweets.data:
                        for tweet in tweets.data:
                            all_tweets.append({
                                'id': tweet.id,
                                'username': username,
                                'display_name': user.data.name,
                                'text': tweet.text,
                                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                                'likes': tweet.public_metrics.get('like_count', 0),
                                'retweets': tweet.public_metrics.get('retweet_count', 0),
                                'replies': tweet.public_metrics.get('reply_count', 0),
                                'profile_image': None
                            })
                except Exception as e:
                    logger.warning(f"Error fetching tweets from {username}: {e}")
                    continue
            
            logger.info(f"Fetched {len(all_tweets)} tweets from public accounts")
            return all_tweets[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching public timeline: {e}")
            return self._get_mock_following_timeline(limit)
    
    async def get_followers_timeline(self, limit: int = 50) -> List[Dict]:
        """Get recent tweets from your followers (using public accounts list)"""
        if self.use_mock:
            return self._get_mock_followers_timeline(limit)
        
        try:
            logger.info("Fetching from public followers accounts list")
            
            # Get accounts from config
            public_accounts = self.config.get('followers_accounts', [])[:10]  # Limit to 10 to avoid rate limits
            
            all_tweets = []
            
            # Fetch recent tweets from each public account
            for username in public_accounts[:5]:  # Process 5 at a time
                try:
                    user = self.client.get_user(username=username)
                    if not user.data:
                        continue
                    
                    tweets = self.client.get_users_tweets(
                        id=user.data.id,
                        max_results=10,
                        tweet_fields=['created_at', 'public_metrics'],
                        exclude=['retweets', 'replies']
                    )
                    
                    if tweets.data:
                        for tweet in tweets.data:
                            all_tweets.append({
                                'id': tweet.id,
                                'username': username,
                                'display_name': user.data.name,
                                'text': tweet.text,
                                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                                'likes': tweet.public_metrics.get('like_count', 0),
                                'retweets': tweet.public_metrics.get('retweet_count', 0),
                                'replies': tweet.public_metrics.get('reply_count', 0),
                                'profile_image': None
                            })
                except Exception as e:
                    logger.warning(f"Error fetching tweets from {username}: {e}")
                    continue
            
            logger.info(f"Fetched {len(all_tweets)} tweets from followers accounts")
            return all_tweets[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching followers timeline: {e}")
            return self._get_mock_followers_timeline(limit)
    
    def _get_mock_following_timeline(self, limit: int) -> List[Dict]:
        """Mock data for following timeline"""
        return [
            {
                'id': 'mock_f1',
                'username': 'TechCrunch',
                'display_name': 'TechCrunch',
                'text': 'Breaking: New 6G wireless standard promises 1Tbps speeds https://techcrunch.com/6g-standard',
                'created_at': '2026-02-12T18:00:00Z',
                'likes': 1250,
                'retweets': 340,
                'replies': 89,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/techcrunch_400x400.jpg'
            },
            {
                'id': 'mock_f2',
                'username': 'Wired',
                'display_name': 'WIRED',
                'text': 'The future of Wi-Fi 7: What you need to know about the next generation of wireless connectivity https://wired.com/wifi7-future',
                'created_at': '2026-02-12T17:30:00Z',
                'likes': 890,
                'retweets': 210,
                'replies': 45,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/wired_400x400.jpg'
            },
            {
                'id': 'mock_f3',
                'username': 'TheVerge',
                'display_name': 'The Verge',
                'text': 'Apple announces new wireless charging technology that works across rooms https://theverge.com/apple-wireless-charging',
                'created_at': '2026-02-12T17:00:00Z',
                'likes': 2100,
                'retweets': 580,
                'replies': 156,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/verge_400x400.jpg'
            },
            {
                'id': 'mock_f4',
                'username': 'engadget',
                'display_name': 'Engadget',
                'text': 'Qualcomm unveils next-gen 5G modem with satellite connectivity https://engadget.com/qualcomm-5g-satellite',
                'created_at': '2026-02-12T16:30:00Z',
                'likes': 670,
                'retweets': 145,
                'replies': 34,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/engadget_400x400.jpg'
            },
            {
                'id': 'mock_f5',
                'username': 'arstechnica',
                'display_name': 'Ars Technica',
                'text': 'Deep dive: How mesh networks are revolutionizing rural connectivity https://arstechnica.com/mesh-networks-rural',
                'created_at': '2026-02-12T16:00:00Z',
                'likes': 445,
                'retweets': 98,
                'replies': 23,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/ars_400x400.jpg'
            }
        ]
    
    def _get_mock_followers_timeline(self, limit: int) -> List[Dict]:
        """Mock data for followers timeline"""
        return [
            {
                'id': 'mock_fo1',
                'username': 'NetworkEngineer',
                'display_name': 'Sarah Chen',
                'text': 'Just deployed a new Wi-Fi 6E network at our campus. The performance improvements are incredible! 🚀',
                'created_at': '2026-02-12T18:15:00Z',
                'likes': 45,
                'retweets': 8,
                'replies': 12,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/default_400x400.jpg'
            },
            {
                'id': 'mock_fo2',
                'username': 'WirelessGuru',
                'display_name': 'Mike Rodriguez',
                'text': 'Interesting article on spectrum allocation challenges: https://ieee.org/spectrum-allocation-2026',
                'created_at': '2026-02-12T17:45:00Z',
                'likes': 67,
                'retweets': 15,
                'replies': 8,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/default_400x400.jpg'
            },
            {
                'id': 'mock_fo3',
                'username': 'TechStartupCEO',
                'display_name': 'Alex Kim',
                'text': 'Our new IoT platform leverages private 5G networks for ultra-low latency. Game changer for industrial automation. https://ourcompany.com/private5g',
                'created_at': '2026-02-12T17:15:00Z',
                'likes': 123,
                'retweets': 34,
                'replies': 19,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/default_400x400.jpg'
            },
            {
                'id': 'mock_fo4',
                'username': 'RFEngineer',
                'display_name': 'Jessica Park',
                'text': 'Fascinating research on beamforming optimization for mmWave 5G: https://arxiv.org/beamforming-mmwave',
                'created_at': '2026-02-12T16:45:00Z',
                'likes': 89,
                'retweets': 21,
                'replies': 14,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/default_400x400.jpg'
            },
            {
                'id': 'mock_fo5',
                'username': 'ConnectivityExpert',
                'display_name': 'David Thompson',
                'text': 'The gap between urban and rural broadband access is still massive. We need better wireless solutions. https://broadbandnow.com/rural-gap-2026',
                'created_at': '2026-02-12T16:20:00Z',
                'likes': 156,
                'retweets': 42,
                'replies': 27,
                'profile_image': 'https://pbs.twimg.com/profile_images/1/default_400x400.jpg'
            }
        ]
    
    async def get_top_stories(self, count: int = 3) -> Dict[str, List[Dict]]:
        """Get top stories from both following and followers"""
        # Fetch timelines
        following_tweets = await self.get_following_timeline()
        followers_tweets = await self.get_followers_timeline()
        
        # Score and sort
        following_scored = [(tweet, self.score_tweet(tweet)) for tweet in following_tweets]
        followers_scored = [(tweet, self.score_tweet(tweet)) for tweet in followers_tweets]
        
        following_scored.sort(key=lambda x: x[1], reverse=True)
        followers_scored.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N with URLs
        top_following = []
        for tweet, score in following_scored:
            if len(top_following) >= count:
                break
            urls = self.extract_urls_from_text(tweet['text'])
            if urls:  # Only include tweets with URLs
                tweet['score'] = score
                tweet['url'] = urls[0]  # Use first URL
                top_following.append(tweet)
        
        top_followers = []
        for tweet, score in followers_scored:
            if len(top_followers) >= count:
                break
            urls = self.extract_urls_from_text(tweet['text'])
            if urls:  # Only include tweets with URLs
                tweet['score'] = score
                tweet['url'] = urls[0]  # Use first URL
                top_followers.append(tweet)
        
        return {
            'following': top_following,
            'followers': top_followers,
            'mode': 'mock' if self.use_mock else 'live'
        }
