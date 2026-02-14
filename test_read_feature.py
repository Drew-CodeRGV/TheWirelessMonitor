#!/usr/bin/env python3
"""Test the read articles feature"""
import requests
import sqlite3

BASE_URL = 'http://localhost:8080'

def test_read_feature():
    print("=" * 80)
    print("TESTING READ ARTICLES FEATURE")
    print("=" * 80)
    print()
    
    # Connect to database
    conn = sqlite3.connect('data/wireless_monitor.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get an unread article
    cursor.execute("SELECT id, title FROM articles WHERE read_status = 0 LIMIT 1")
    article = cursor.fetchone()
    
    if not article:
        print("❌ No unread articles found")
        conn.close()
        return
    
    article_id = article['id']
    article_title = article['title']
    
    print(f"Test Article ID: {article_id}")
    print(f"Test Article: {article_title[:60]}...")
    print()
    
    # Test 1: Mark as read
    print("Test 1: Mark article as read")
    response = requests.post(f'{BASE_URL}/api/mark_as_read', json={'article_id': article_id})
    data = response.json()
    
    if data.get('success'):
        print("✅ API call successful")
        
        # Verify in database
        cursor.execute("SELECT read_status FROM articles WHERE id = ?", (article_id,))
        status = cursor.fetchone()['read_status']
        
        if status == 1:
            print("✅ Article marked as read in database")
        else:
            print("❌ Article not marked as read in database")
    else:
        print(f"❌ API call failed: {data.get('error')}")
    
    print()
    
    # Test 2: Mark as unread
    print("Test 2: Mark article as unread")
    response = requests.post(f'{BASE_URL}/api/mark_as_unread', json={'article_id': article_id})
    data = response.json()
    
    if data.get('success'):
        print("✅ API call successful")
        
        # Verify in database
        cursor.execute("SELECT read_status FROM articles WHERE id = ?", (article_id,))
        status = cursor.fetchone()['read_status']
        
        if status == 0:
            print("✅ Article marked as unread in database")
        else:
            print("❌ Article not marked as unread in database")
    else:
        print(f"❌ API call failed: {data.get('error')}")
    
    print()
    
    # Test 3: Mark multiple as read
    print("Test 3: Mark multiple articles as read")
    cursor.execute("SELECT id FROM articles WHERE read_status = 0 LIMIT 3")
    article_ids = [row['id'] for row in cursor.fetchall()]
    
    if article_ids:
        response = requests.post(f'{BASE_URL}/api/mark_all_as_read', json={'article_ids': article_ids})
        data = response.json()
        
        if data.get('success'):
            print(f"✅ API call successful - marked {len(article_ids)} articles")
            
            # Verify in database
            placeholders = ','.join('?' * len(article_ids))
            cursor.execute(f"SELECT COUNT(*) as count FROM articles WHERE id IN ({placeholders}) AND read_status = 1", article_ids)
            count = cursor.fetchone()['count']
            
            if count == len(article_ids):
                print(f"✅ All {len(article_ids)} articles marked as read in database")
            else:
                print(f"❌ Only {count}/{len(article_ids)} articles marked as read")
        else:
            print(f"❌ API call failed: {data.get('error')}")
    else:
        print("⚠️  No unread articles to test with")
    
    print()
    
    # Test 4: Check read articles count
    print("Test 4: Check read articles statistics")
    cursor.execute("SELECT COUNT(*) as count FROM articles WHERE read_status = 1")
    read_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM articles WHERE read_status = 0")
    unread_count = cursor.fetchone()['count']
    
    print(f"📚 Read articles: {read_count}")
    print(f"📰 Unread articles: {unread_count}")
    print(f"📊 Total articles: {read_count + unread_count}")
    
    print()
    
    # Test 5: Check read articles page
    print("Test 5: Check read articles page")
    response = requests.get(f'{BASE_URL}/read_articles')
    
    if response.status_code == 200:
        print("✅ Read articles page accessible")
        if 'Read Articles' in response.text:
            print("✅ Page contains expected content")
        else:
            print("⚠️  Page may not be rendering correctly")
    else:
        print(f"❌ Read articles page returned status {response.status_code}")
    
    conn.close()
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("You can now:")
    print("1. Visit http://localhost:8080 to see the main headlines")
    print("2. Click '✓ Read' on any article to mark it as read")
    print("3. Click '✓ Mark All Read' to mark all visible articles")
    print("4. Click '📚 Read' in navigation to view read articles")
    print("5. Click 'Mark Unread' to restore articles to main feed")

if __name__ == '__main__':
    test_read_feature()
