import asyncio
import sys
sys.path.insert(0, 'app')

from enhancements import EnhancedImageScraper

async def test_scraper():
    scraper = EnhancedImageScraper()
    
    # Test URLs
    test_urls = [
        ("https://www.rcrwireless.com/20260212/5g/uk-5g-sa-investment", "UK 5G SA Investment"),
        ("https://www.wired.com/review/samsung-galaxy-a17-5g/", "Samsung Galaxy A17 5G Review"),
        ("https://www.engadget.com/deals/presidents-day-sales-2026-the-best-tech-deals-to-shop-this-week-from-apple-sony-samsung-and-others-163000831.html", "Presidents Day Sales"),
    ]
    
    for url, title in test_urls:
        print(f"\n{'='*80}")
        print(f"Testing: {title}")
        print(f"URL: {url}")
        print(f"{'='*80}")
        
        result = await scraper.scrape_article_image(url, title)
        
        if result and result.get('image_url'):
            print(f"\n✅ SUCCESS!")
            print(f"   Strategy: {result.get('strategy')}")
            print(f"   Image URL: {result['image_url']}")
            print(f"   Cached: {result.get('cached', False)}")
            
            if result.get('metadata'):
                meta = result['metadata']
                print(f"   Dimensions: {meta.get('width')}x{meta.get('height')}")
                print(f"   File Size: {meta.get('file_size')} bytes")
                print(f"   Content Type: {meta.get('content_type')}")
        else:
            print(f"\n❌ FAILED - No image found")
    
    await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(test_scraper())
