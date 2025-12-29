#!/usr/bin/env python3
"""
AI-powered article analysis for Wi-Fi/Wireless relevance
"""

import requests
import json
import logging
from models import get_db_connection
import re
from collections import Counter
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.wifi_keywords = [
            'wifi', 'wi-fi', 'wireless', '802.11', 'bluetooth', '5g', '6g', 'lte',
            'cellular', 'antenna', 'spectrum', 'frequency', 'band', 'router',
            'access point', 'mesh', 'networking', 'connectivity', 'broadband',
            'telecommunications', 'radio', 'signal', 'interference', 'latency',
            'bandwidth', 'throughput', 'iot', 'internet of things', 'smart home',
            'connected devices', 'wireless charging', 'nfc', 'zigbee', 'thread',
            'matter', 'homekit', 'alexa', 'google home', 'smart speaker',
            'wireless security', 'wpa3', 'encryption', 'cybersecurity'
        ]
        
        # Entertainment indicators for wireless/tech stories
        self.entertainment_keywords = [
            'funny', 'hilarious', 'bizarre', 'weird', 'strange', 'unusual',
            'fail', 'epic', 'viral', 'meme', 'joke', 'prank', 'hack',
            'creative', 'innovative', 'cool', 'awesome', 'amazing',
            'record', 'fastest', 'longest', 'biggest', 'smallest',
            'art', 'music', 'game', 'gaming', 'entertainment', 'fun',
            'celebrity', 'famous', 'trending', 'social media', 'tiktok',
            'youtube', 'instagram', 'twitter', 'reddit'
        ]
        
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Drew Lentz voice characteristics based on research
        self.drew_voice_profile = {
            'tone': 'conversational and approachable',
            'expertise': 'deep technical knowledge explained simply',
            'personality': 'passionate wireless enthusiast with practical experience',
            'style': 'candid, real-world examples, problem-solving focused',
            'catchphrases': ['making waves', 'wireless world', 'at the end of the day'],
            'background': '20+ years data delivery, decade in wireless, field deployment experience',
            'approach': 'simplifies complex concepts, uses trade show and meeting room analogies'
        }
        
    def analyze_articles(self, article_ids):
        """Analyze articles for Wi-Fi/wireless relevance and entertainment value"""
        if not article_ids:
            return 0
            
        conn = get_db_connection()
        analyzed_count = 0
        
        for article_id in article_ids:
            try:
                # Get article content
                article = conn.execute('''
                    SELECT id, title, description, content FROM articles WHERE id = ?
                ''', (article_id,)).fetchone()
                
                if not article:
                    continue
                
                # Combine text for analysis
                text = f"{article['title']} {article['description']} {article['content']}"
                
                # Calculate relevance score
                relevance_score = self.calculate_relevance_score(text)
                
                # Calculate entertainment score
                entertainment_score = self.calculate_entertainment_score(text)
                
                # Extract matching keywords
                matching_keywords = self.extract_matching_keywords(text)
                
                # Get AI summary if highly relevant
                ai_summary = ""
                if relevance_score > 0.7:
                    ai_summary = self.get_ai_summary(text)
                
                # Update article with analysis
                conn.execute('''
                    UPDATE articles 
                    SET relevance_score = ?, entertainment_score = ?, wifi_keywords = ?
                    WHERE id = ?
                ''', (relevance_score, entertainment_score, json.dumps(matching_keywords), article_id))
                
                analyzed_count += 1
                logger.info(f"Analyzed article {article_id}: relevance {relevance_score:.2f}, entertainment {entertainment_score:.2f}")
                
            except Exception as e:
                logger.error(f"Error analyzing article {article_id}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return analyzed_count
    
    def calculate_relevance_score(self, text):
        """Calculate relevance score based on keyword matching and context"""
        text_lower = text.lower()
        
        # Count keyword matches
        keyword_matches = 0
        matched_keywords = []
        
        for keyword in self.wifi_keywords:
            if keyword in text_lower:
                keyword_matches += 1
                matched_keywords.append(keyword)
        
        # Base score from keyword density
        word_count = len(text.split())
        keyword_density = keyword_matches / max(word_count, 1) * 100
        
        # Boost score for important keywords
        important_keywords = ['wifi', 'wi-fi', 'wireless', '5g', '6g', '802.11']
        important_matches = sum(1 for kw in important_keywords if kw in text_lower)
        
        # Calculate final score (0.0 to 1.0)
        base_score = min(keyword_density * 10, 0.8)  # Cap at 0.8 from keywords alone
        importance_boost = min(important_matches * 0.1, 0.3)  # Up to 0.3 boost
        
        final_score = min(base_score + importance_boost, 1.0)
        
        return round(final_score, 3)
    
    def calculate_entertainment_score(self, text):
        """Calculate entertainment value score for wireless/tech stories"""
        text_lower = text.lower()
        
        # Count entertainment keyword matches
        entertainment_matches = 0
        for keyword in self.entertainment_keywords:
            if keyword in text_lower:
                entertainment_matches += 1
        
        # Look for entertainment patterns
        entertainment_patterns = [
            r'\b(went viral|breaking the internet|social media buzz)\b',
            r'\b(record.{0,20}(speed|distance|size))\b',
            r'\b(fail|epic|amazing|incredible|unbelievable)\b',
            r'\b(creative|innovative|genius|brilliant)\s+(hack|solution|idea)\b',
            r'\b(funny|hilarious|bizarre|weird)\s+(story|incident|case)\b'
        ]
        
        pattern_matches = 0
        for pattern in entertainment_patterns:
            if re.search(pattern, text_lower):
                pattern_matches += 1
        
        # Calculate entertainment score (0.0 to 1.0)
        base_score = min(entertainment_matches * 0.1, 0.6)  # Up to 0.6 from keywords
        pattern_boost = min(pattern_matches * 0.15, 0.4)    # Up to 0.4 from patterns
        
    def extract_matching_keywords(self, text):
        """Extract keywords that match from the text"""
        text_lower = text.lower()
        matching = []
        
        for keyword in self.wifi_keywords:
            if keyword in text_lower:
                matching.append(keyword)
        
        return matching
    
    def get_ai_summary(self, text):
        """Get AI-generated summary using Ollama (if available)"""
        try:
            prompt = f"""
            Summarize this technology article in 2-3 sentences, focusing on the key wireless/Wi-Fi/networking aspects:
            
            {text[:2000]}  # Limit text length
            """
            
            payload = {
                "model": "llama2",  # or whatever model is installed
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 150
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.warning(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.warning(f"Could not get AI summary: {str(e)}")
            return ""
    
    def generate_weekly_digest(self):
        """Generate weekly digest of top stories"""
        conn = get_db_connection()
        
        # Get top stories from last 7 days
        stories = conn.execute('''
            SELECT title, url, description, relevance_score, published_date
            FROM articles 
            WHERE published_date >= date('now', '-7 days')
            AND relevance_score > 0.6
            ORDER BY relevance_score DESC, published_date DESC
            LIMIT 20
        ''').fetchall()
        
        if not stories:
            return "No significant wireless/Wi-Fi stories this week."
        
        # Create digest summary
        digest_text = "Weekly Wi-Fi & Wireless Technology Digest\n\n"
        digest_text += f"Top {len(stories)} stories from the past week:\n\n"
        
        for i, story in enumerate(stories, 1):
            digest_text += f"{i}. {story['title']}\n"
            digest_text += f"   Relevance: {story['relevance_score']:.2f}\n"
            digest_text += f"   {story['description'][:200]}...\n"
            digest_text += f"   {story['url']}\n\n"
        
        # Store digest
        conn.execute('''
            INSERT INTO weekly_digests (week_start, week_end, summary, top_stories)
            VALUES (date('now', '-7 days'), date('now'), ?, ?)
        ''', (digest_text, json.dumps([dict(story) for story in stories])))
        
        conn.commit()
        conn.close()
        
        return digest_text

    def generate_podcast_script(self, week_start_date):
        """Generate podcast script in Drew Lentz's voice for weekly stories"""
        try:
            conn = get_db_connection()
            
            # Get top stories from the week
            stories = conn.execute('''
                SELECT title, url, description, relevance_score, entertainment_score, published_date
                FROM articles 
                WHERE DATE(published_date) >= DATE(?) 
                AND DATE(published_date) < DATE(?, '+7 days')
                AND relevance_score > 0.5
                ORDER BY relevance_score DESC, entertainment_score DESC
                LIMIT 15
            ''', (week_start_date, week_start_date)).fetchall()
            
            if not stories:
                return "No significant wireless stories this week for the podcast."
            
            # Separate stories by type
            top_stories = [s for s in stories if s['relevance_score'] > 0.8][:5]
            entertaining_stories = [s for s in stories if s['entertainment_score'] > 0.5][:3]
            
            # Generate script using AI with Drew's voice profile
            script_prompt = f"""
            Write a podcast script for "Waves with Wireless Nerd" hosted by Drew Lentz. 

            Drew's Voice Profile:
            - 20+ years in data delivery, decade focused on wireless deployments
            - Explains complex tech concepts with real-world examples
            - Conversational, passionate, practical problem-solver
            - Uses phrases like "making waves", "at the end of the day", "wireless world"
            - Candid about technology, focuses on solutions
            - Background in field deployments, trade shows, meeting rooms
            
            This week's top wireless stories:
            {chr(10).join([f"- {s['title']}: {s['description'][:200]}..." for s in top_stories])}
            
            Fun/entertaining wireless stories:
            {chr(10).join([f"- {s['title']}: {s['description'][:150]}..." for s in entertaining_stories])}
            
            Create a 10-15 minute script that:
            1. Opens with Drew's signature style
            2. Covers the top technical stories with his practical insights
            3. Includes the entertaining stories with his commentary
            4. Closes with industry outlook and community engagement
            5. Sounds natural and conversational, like Drew is speaking to wireless professionals
            
            Keep Drew's tone: knowledgeable but approachable, passionate about wireless, focused on real-world applications.
            """
            
            script = self.get_ai_response(script_prompt, max_tokens=2000)
            
            # Store the script
            conn.execute('''
                UPDATE weekly_digests 
                SET podcast_script = ?
                WHERE week_start = DATE(?)
            ''', (script, week_start_date))
            
            # If no weekly digest exists, create one
            if conn.rowcount == 0:
                conn.execute('''
                    INSERT INTO weekly_digests (week_start, week_end, podcast_script)
                    VALUES (DATE(?), DATE(?, '+6 days'), ?)
                ''', (week_start_date, week_start_date, script))
            
            conn.commit()
            conn.close()
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating podcast script: {e}")
            return f"Error generating podcast script: {str(e)}"
    
    def get_ai_response(self, prompt, max_tokens=500):
        """Get AI response with better error handling and longer responses"""
        try:
            payload = {
                "model": "llama2:7b-chat",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.warning(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.warning(f"Could not get AI response: {str(e)}")
            return ""
    
    def get_entertainment_stories(self, days=7):
        """Get entertaining wireless stories from recent days"""
        try:
            conn = get_db_connection()
            
            stories = conn.execute('''
                SELECT title, url, description, entertainment_score, relevance_score, published_date
                FROM articles 
                WHERE DATE(published_date) >= DATE('now', '-{} days')
                AND entertainment_score > 0.4
                AND relevance_score > 0.3
                ORDER BY entertainment_score DESC, relevance_score DESC
                LIMIT 10
            '''.format(days)).fetchall()
            
            conn.close()
            return [dict(story) for story in stories]
            
        except Exception as e:
            logger.error(f"Error getting entertainment stories: {e}")
            return []