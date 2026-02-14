"""
Test the full image scraping flow from article URL to database
"""
import sqlite3
import asyncio
import sys
sys.path.insert(0, 'app')

from enhancements import EnhancedImageScraper

# Test URLs from different sources
TEST_ARTICLES = [
    {
        'title': 'UK launches consultation to unlock 5G SA investment',
        'url': 'https://www.rcrwireless.com/20260212/5g/uk-5g-sa-investment',
        'source': 'RCR Wireless'
    },
    {
        'title': 'Samsung Galaxy A17 5G Review',
        'url': 'https://www.wired.com/review/samsung-galaxy-a17-5g/',
        'source': 'Wired'
    },
    {
        'title': 'Presidents Day Sales 2026',
        'url': 'https://www.engadget.com/deals/presidents-day-sales-2026-the-best-tech-deals-to-shop-this-week-from-apple-sony-samsung-and-others-163000831.html',
        'source': 'Engadget'
    }
]

async def test_full_flow():
    """Test the complete image scraping and storage flow"""
    
    # Initialize scraper
    scraper = EnhancedImageScraper()
    
    print("=" * 80)
    print("FULL IMAGE SCRAPING FLOW TEST")
    print("=" * 80)
    print()
    
    # Connect to database
    conn = sqlite3.connect('data/wireless_monitor.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    results = []
    
    for article in TEST_ARTICLES:
        print(f"\n{'=' * 80}")
        print(f"Testing: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"URL: {article['url']}")
        print(f"{'=' * 80}\n")
        
        # Scrape image
        result = await scraper.scrape_article_image(article['url'], article['title'])
        
        if result and result.get('image_url'):
            print(f"✅ SUCCESS!")
            print(f"   Strategy: {result.get('strategy')}")
            print(f"   Image URL: {result['image_url'][:100]}...")
            print(f"   Cached: {result.get('cached', False)}")
            
            if result.get('metadata'):
                meta = result['metadata']
                print(f"   Dimensions: {meta.get('width')}x{meta.get('height')}")
                print(f"   File Size: {meta.get('file_size')} bytes")
                print(f"   Content Type: {meta.get('content_type')}")
            
            # Test database storage
            try:
                # Create a test article entry
                cursor.execute("""
                    INSERT OR IGNORE INTO articles (title, url, published_date, source, image_url)
                    VALUES (?, ?, datetime('now'), ?, ?)
                """, (article['title'], article['url'], article['source'], result['image_url']))
                
                article_id = cursor.lastrowid
                
                # Store metadata
                if result.get('metadata') and article_id:
                    metadata = result['metadata']
                    cursor.execute("""
                        INSERT OR REPLACE INTO image_metadata
                        (article_id, image_url, extraction_strategy, width, height, file_size, content_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article_id,
                        result['image_url'],
                        result.get('strategy'),
                        metadata.get('width'),
                        metadata.get('height'),
                        metadata.get('file_size'),
                        metadata.get('content_type')
                    ))
                    print(f"   ✅ Metadata stored in database (article_id: {article_id})")
                
                conn.commit()
                
                results.append({
                    'article': article,
                    'success': True,
                    'image_url': result['image_url'],
                    'strategy': result.get('strategy')
                })
                
            except Exception as e:
                print(f"   ⚠️  Database error: {e}")
                results.append({
                    'article': article,
                    'success': False,
                    'error': str(e)
                })
        else:
            print(f"❌ FAILED - No image found")
            results.append({
                'article': article,
                'success': False,
                'error': 'No image found'
            })
    
    conn.close()
    
    # Summary
    print(f"\n\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")
    
    success_count = sum(1 for r in results if r['success'])
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print()
    
    for r in results:
        status = "✅" if r['success'] else "❌"
        source = r['article']['source']
        if r['success']:
            print(f"{status} {source:15} - {r['strategy']}")
        else:
            print(f"{status} {source:15} - {r.get('error', 'Unknown error')}")

if __name__ == '__main__':
    asyncio.run(test_full_flow())
