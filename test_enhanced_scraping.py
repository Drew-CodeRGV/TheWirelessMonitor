#!/usr/bin/env python3
"""
Test the enhanced image scraping on real articles
"""

import sys
import os
sys.path.append('app')

from main import WirelessMonitor
import sqlite3

def test_enhanced_scraping():
    print("🔍 Testing Enhanced Image Scraping")
    print("=" * 50)
    
    # Initialize the scraper
    monitor = WirelessMonitor()
    
    # Get some real articles to test
    conn = sqlite3.connect('data/wireless_monitor.db')
    articles = conn.execute('''
        SELECT id, title, url FROM articles 
        WHERE url LIKE '%arstechnica%' OR url LIKE '%engadget%' OR url LIKE '%techcrunch%'
        ORDER BY id DESC LIMIT 5
    ''').fetchall()
    conn.close()
    
    if not articles:
        print("❌ No real articles found to test")
        return
    
    print(f"📰 Testing {len(articles)} real articles:")
    
    for i, (article_id, title, url) in enumerate(articles, 1):
        print(f"\n🔍 [{i}/{len(articles)}] Testing: {title[:60]}...")
        print(f"🔗 URL: {url}")
        
        try:
            # Test the enhanced scraping
            image_url = monitor.scrape_article_image(url, title)
            
            if image_url:
                print(f"✅ SUCCESS: {image_url}")
                
                # Update the database with the new image
                conn = sqlite3.connect('data/wireless_monitor.db')
                conn.execute('UPDATE articles SET image_url = ? WHERE id = ?', (image_url, article_id))
                conn.commit()
                conn.close()
                print(f"💾 Updated database for article {article_id}")
            else:
                print(f"❌ FAILED: No image found")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced scraping test completed!")

if __name__ == "__main__":
    test_enhanced_scraping()