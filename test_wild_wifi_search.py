#!/usr/bin/env python3
"""Test Wild Wi-Fi news search functionality"""

import sys
import os
import sqlite3

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from main import WirelessMonitor

def test_search():
    """Test the Wild Wi-Fi news search"""
    print("🔍 Testing Wild Wi-Fi News Search")
    print("=" * 60)
    
    # Initialize the app
    app = WirelessMonitor()
    
    # Get database connection
    conn = app.get_db_connection()
    
    # Test search with a sample keyword
    test_keyword = "wifi password funny"
    print(f"\n📡 Searching for: '{test_keyword}'")
    print("-" * 60)
    
    try:
        stories_found = app.search_and_save_wild_wifi_stories(conn, test_keyword)
        
        print(f"\n✅ Search completed!")
        print(f"   Stories found and saved: {stories_found}")
        
        if stories_found > 0:
            # Show the stories
            print("\n📰 New Stories:")
            print("-" * 60)
            
            cursor = conn.execute('''
                SELECT title, category, location, quality_score, humor_rating
                FROM wild_wifi_stories
                ORDER BY created_at DESC
                LIMIT ?
            ''', (stories_found,))
            
            for i, row in enumerate(cursor.fetchall(), 1):
                title, category, location, quality, humor = row
                print(f"\n{i}. {title}")
                print(f"   Category: {category}")
                print(f"   Location: {location}")
                print(f"   Quality: {quality:.1f}/100 | Humor: {humor}/10")
        else:
            print("\n⚠️  No new stories found (may already exist or no results)")
        
        # Show total stories in database
        total = conn.execute('SELECT COUNT(*) FROM wild_wifi_stories').fetchone()[0]
        print(f"\n📊 Total Wild Wi-Fi stories in database: {total}")
        
    except Exception as e:
        print(f"\n❌ Error during search: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")

if __name__ == '__main__':
    test_search()
