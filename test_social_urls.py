#!/usr/bin/env python3
"""
Test script to verify that social sharing includes article URLs properly
"""

import requests
import json
import urllib.parse

def test_social_urls():
    base_url = "http://localhost:8080"
    
    print("🔗 Testing Social Sharing URL Integration")
    print("=" * 50)
    
    # Get a sample article
    try:
        import sqlite3
        conn = sqlite3.connect('app/data/wireless_monitor.db')
        article = conn.execute('SELECT id, title, url FROM articles LIMIT 1').fetchone()
        conn.close()
        
        if not article:
            print("❌ No articles found")
            return False
            
        article_id, article_title, article_url = article
        print(f"📰 Testing with article: {article_title[:50]}...")
        print(f"🔗 Original URL: {article_url}")
        
    except Exception as e:
        print(f"❌ Error getting article: {e}")
        return False
    
    # Test each platform
    platforms = ['Twitter', 'LinkedIn', 'Facebook', 'Mastodon', 'Instagram']
    
    for platform in platforms:
        print(f"\n📱 Testing {platform}:")
        
        try:
            response = requests.post(
                f"{base_url}/api/share_article",
                headers={'Content-Type': 'application/json'},
                json={'article_id': article_id, 'platform': platform}
            )
            data = response.json()
            
            if not data['success']:
                print(f"   ❌ API Error: {data.get('error', 'Unknown error')}")
                continue
                
            share_content = data['share_content']
            content = share_content['content']
            share_url = share_content['share_url']
            
            # Check if URL is in content
            url_in_content = article_url in content
            
            # Check if URL is in share_url (for platforms that use URL parameters)
            url_in_share_url = article_url in share_url
            
            # Platform-specific checks
            if platform == 'Twitter':
                # Twitter should have URL in share_url parameter
                parsed_url = urllib.parse.urlparse(share_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                has_url_param = 'url' in query_params and article_url in query_params['url'][0]
                
                if has_url_param and url_in_content:
                    print(f"   ✅ URL properly included in both content preview and share URL")
                elif has_url_param:
                    print(f"   ✅ URL in share URL parameter (Twitter will add it automatically)")
                else:
                    print(f"   ❌ URL missing from share URL parameter")
                    
            elif platform == 'Facebook':
                # Facebook should have URL in 'u' parameter
                parsed_url = urllib.parse.urlparse(share_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                has_url_param = 'u' in query_params and article_url in query_params['u'][0]
                
                if has_url_param and url_in_content:
                    print(f"   ✅ URL properly included in both content preview and share URL")
                elif has_url_param:
                    print(f"   ✅ URL in share URL parameter (Facebook will add it automatically)")
                else:
                    print(f"   ❌ URL missing from share URL parameter")
                    
            else:
                # LinkedIn, Mastodon, Instagram should have URL in content
                if url_in_content:
                    print(f"   ✅ URL properly included in share content")
                else:
                    print(f"   ❌ URL missing from share content")
            
            # Show preview of content (first 100 chars)
            print(f"   📝 Content preview: {content[:100]}...")
            
            # Show if URL is visible
            if '🔗' in content:
                print(f"   🔗 URL clearly marked with link emoji")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Social URL integration test completed!")
    return True

if __name__ == "__main__":
    test_social_urls()