#!/usr/bin/env python3
"""
Test the enhanced image scraping specifically on Ars Technica articles
"""

import sys
import os
sys.path.append('app')

from main import WirelessMonitor
import sqlite3

def test_ars_scraping():
    print("🔍 Testing Enhanced Scraping on Ars Technica")
    print("=" * 50)
    
    # Initialize the scraper
    monitor = WirelessMonitor()
    
    # Get Ars Technica articles
    conn = sqlite3.connect('data/wireless_monitor.db')
    articles = conn.execute('''
        SELECT id, title, url FROM articles 
        WHERE url LIKE '%arstechnica%'
        ORDER BY id DESC LIMIT 3
    ''').fetchall()
    conn.close()
    
    if not articles:
        print("❌ No Ars Technica articles found")
        return
    
    print(f"📰 Testing {len(articles)} Ars Technica articles:")
    
    for i, (article_id, title, url) in enumerate(articles, 1):
        print(f"\n🔍 [{i}/{len(articles)}] Testing: {title[:60]}...")
        print(f"🔗 URL: {url}")
        
        try:
            # Test the enhanced scraping
            image_url = monitor.scrape_article_image(url, title)
            
            if image_url:
                print(f"✅ SUCCESS: {image_url}")
                
                # Check if it's a real Ars Technica image
                if 'arstechnica' in image_url.lower():
                    print(f"🎯 PERFECT: Real Ars Technica image!")
                elif any(host in image_url.lower() for host in ['yimg.com', 'cloudfront.net']):
                    print(f"📰 GOOD: News site image")
                else:
                    print(f"🔄 FALLBACK: External image")
                
                # Update the database
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
    print("🎉 Ars Technica scraping test completed!")

if __name__ == "__main__":
    test_ars_scraping()