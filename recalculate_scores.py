#!/usr/bin/env python3
"""
Recalculate Waves scores for all articles using the new algorithm
Run this after updating the scoring logic
"""

import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, '.')

from app.main import WirelessMonitor

def recalculate_all_scores():
    """Recalculate scores for all recent articles"""
    print("=" * 60)
    print("Recalculating Waves Scores")
    print("=" * 60)
    
    monitor = WirelessMonitor()
    conn = monitor.get_db_connection()
    
    # Get all articles (not just last 7 days - we want to recalculate everything)
    articles = conn.execute('''
        SELECT id, title, published_date 
        FROM articles 
        ORDER BY published_date DESC
    ''').fetchall()
    
    print(f"\nFound {len(articles)} articles to process\n")
    
    scores = []
    
    for i, article in enumerate(articles, 1):
        try:
            score = monitor.calculate_waves_score(article['id'], conn)
            scores.append(score)
            
            if i % 10 == 0:
                print(f"Processed {i}/{len(articles)} articles...")
        except Exception as e:
            print(f"Error processing article {article['id']}: {e}")
    
    conn.close()
    
    # Show statistics
    print("\n" + "=" * 60)
    print("Score Distribution")
    print("=" * 60)
    
    if scores:
        scores.sort(reverse=True)
        
        print(f"Total articles: {len(scores)}")
        print(f"Highest score: {scores[0]:.1f}")
        print(f"Lowest score: {scores[-1]:.1f}")
        print(f"Average score: {sum(scores)/len(scores):.1f}")
        print(f"Median score: {scores[len(scores)//2]:.1f}")
        
        # Show distribution
        high = sum(1 for s in scores if s >= 80)
        medium = sum(1 for s in scores if 50 <= s < 80)
        low = sum(1 for s in scores if s < 50)
        
        print(f"\n🟢 High (80+): {high} articles ({high/len(scores)*100:.1f}%)")
        print(f"🟠 Medium (50-79): {medium} articles ({medium/len(scores)*100:.1f}%)")
        print(f"⚫ Low (<50): {low} articles ({low/len(scores)*100:.1f}%)")
        
        # Show top 10
        print("\n" + "=" * 60)
        print("Top 10 Articles")
        print("=" * 60)
        
        conn = monitor.get_db_connection()
        top_articles = conn.execute('''
            SELECT title, waves_score, cross_source_count, feed_id
            FROM articles
            ORDER BY waves_score DESC
            LIMIT 10
        ''').fetchall()
        
        for i, article in enumerate(top_articles, 1):
            feed = conn.execute('SELECT name FROM rss_feeds WHERE id = ?', (article['feed_id'],)).fetchone()
            feed_name = feed['name'] if feed else 'Unknown'
            print(f"\n{i}. Score: {article['waves_score']:.1f} | Sources: {article['cross_source_count']}")
            print(f"   {article['title'][:80]}")
            print(f"   ({feed_name})")
        
        conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Recalculation complete!")
    print("=" * 60)

if __name__ == '__main__':
    recalculate_all_scores()
