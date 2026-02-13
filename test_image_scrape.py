import requests
from bs4 import BeautifulSoup
import json

# Test URL from RCR Wireless
test_url = "https://www.rcrwireless.com/20260212/5g/uk-5g-sa-investment"

print(f"\n=== Testing Image Scraping for: {test_url} ===\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

try:
    response = requests.get(test_url, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check Open Graph
        print("\n1. Open Graph Images:")
        og_images = soup.find_all('meta', property='og:image')
        for img in og_images:
            print(f"   - {img.get('content')}")
        
        # Check Twitter Card
        print("\n2. Twitter Card Images:")
        twitter_images = soup.find_all('meta', attrs={'name': 'twitter:image'})
        for img in twitter_images:
            print(f"   - {img.get('content')}")
        
        # Check JSON-LD
        print("\n3. JSON-LD Structured Data:")
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if 'image' in data:
                    print(f"   - {data['image']}")
            except:
                pass
        
        # Check article images
        print("\n4. Article Images (first 5):")
        article_imgs = soup.find_all('img', limit=10)
        for img in article_imgs:
            src = img.get('src') or img.get('data-src')
            if src and not any(x in src.lower() for x in ['logo', 'icon', 'avatar']):
                print(f"   - {src}")
                print(f"     Alt: {img.get('alt', 'N/A')}")
                print(f"     Class: {img.get('class', 'N/A')}")
        
        # Check featured image
        print("\n5. Featured/Hero Images:")
        featured = soup.find_all(['img'], class_=lambda x: x and any(term in str(x).lower() for term in ['featured', 'hero', 'main', 'article', 'post']))
        for img in featured:
            src = img.get('src') or img.get('data-src')
            if src:
                print(f"   - {src}")
        
        # Check figure elements
        print("\n6. Figure Elements:")
        figures = soup.find_all('figure')
        for fig in figures:
            img = fig.find('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src:
                    print(f"   - {src}")
    
except Exception as e:
    print(f"Error: {e}")
