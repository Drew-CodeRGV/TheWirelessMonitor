"""
Validate that the enhanced image scraper is properly integrated
"""
import sqlite3
import asyncio
import sys
sys.path.insert(0, 'app')

from enhancements import EnhancedImageScraper

async def validate_integration():
    """Validate the enhanced scraper integration"""
    
    print("=" * 80)
    print("ENHANCED IMAGE SCRAPER INTEGRATION VALIDATION")
    print("=" * 80)
    print()
    
    # Test 1: Scraper initialization
    print("Test 1: Scraper Initialization")
    try:
        scraper = EnhancedImageScraper()
        print("✅ Enhanced scraper initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        return
    
    print()
    
    # Test 2: Image extraction from different sources
    print("Test 2: Multi-Source Image Extraction")
    test_urls = [
        ('RCR Wireless', 'https://www.rcrwireless.com/20260212/5g/uk-5g-sa-investment'),
        ('Wired', 'https://www.wired.com/review/samsung-galaxy-a17-5g/'),
        ('Engadget', 'https://www.engadget.com/deals/presidents-day-sales-2026-the-best-tech-deals-to-shop-this-week-from-apple-sony-samsung-and-others-163000831.html')
    ]
    
    results = []
    for source, url in test_urls:
        result = await scraper.scrape_article_image(url, f"Test article from {source}")
        if result and result.get('image_url'):
            print(f"✅ {source:15} - {result.get('strategy'):12} - {result['image_url'][:60]}...")
            results.append(True)
        else:
            print(f"❌ {source:15} - Failed to extract image")
            results.append(False)
    
    print()
    
    # Test 3: Database schema validation
    print("Test 3: Database Schema Validation")
    try:
        conn = sqlite3.connect('data/wireless_monitor.db')
        cursor = conn.cursor()
        
        # Check for image_metadata table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_metadata'")
        if cursor.fetchone():
            print("✅ image_metadata table exists")
        else:
            print("❌ image_metadata table missing")
        
        # Check for required columns
        cursor.execute("PRAGMA table_info(image_metadata)")
        columns = [row[1] for row in cursor.fetchall()]
        required_columns = ['article_id', 'image_url', 'extraction_strategy', 'width', 'height', 'file_size', 'content_type']
        
        missing = [col for col in required_columns if col not in columns]
        if not missing:
            print(f"✅ All required columns present: {', '.join(required_columns)}")
        else:
            print(f"❌ Missing columns: {', '.join(missing)}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
    
    print()
    
    # Test 4: Check recent articles in database
    print("Test 4: Recent Articles Image Status")
    try:
        conn = sqlite3.connect('data/wireless_monitor.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, image_url, 
                   CASE 
                       WHEN image_url LIKE '%unsplash%' THEN 'Fallback'
                       WHEN image_url IS NULL THEN 'None'
                       ELSE 'Real'
                   END as image_type
            FROM articles 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        articles = cursor.fetchall()
        for article in articles:
            print(f"  Article {article['id']:3}: {article['image_type']:8} - {article['title'][:50]}")
        
        # Count image types
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN image_url LIKE '%unsplash%' THEN 1 ELSE 0 END) as fallback,
                SUM(CASE WHEN image_url IS NULL THEN 1 ELSE 0 END) as none,
                SUM(CASE WHEN image_url NOT LIKE '%unsplash%' AND image_url IS NOT NULL THEN 1 ELSE 0 END) as real
            FROM articles
        """)
        
        stats = cursor.fetchone()
        print()
        print(f"  Total Articles: {stats['total']}")
        print(f"  Real Images: {stats['real']} ({stats['real']/stats['total']*100:.1f}%)")
        print(f"  Fallback Images: {stats['fallback']} ({stats['fallback']/stats['total']*100:.1f}%)")
        print(f"  No Images: {stats['none']} ({stats['none']/stats['total']*100:.1f}%)")
        
        conn.close()
    except Exception as e:
        print(f"❌ Article check failed: {e}")
    
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    success_rate = sum(results) / len(results) * 100 if results else 0
    print(f"Image Extraction Success Rate: {success_rate:.0f}%")
    
    if success_rate == 100:
        print("✅ Enhanced image scraper is fully operational!")
        print()
        print("NEXT STEPS:")
        print("1. Wait for new RSS articles to be fetched (every 6 hours)")
        print("2. Or manually trigger fetch via: http://localhost:8080/api/fetch_now")
        print("3. New articles will automatically use the enhanced scraper")
    else:
        print("⚠️  Some image extraction tests failed")

if __name__ == '__main__':
    asyncio.run(validate_integration())
