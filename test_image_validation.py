import requests
from PIL import Image
from io import BytesIO

test_image_url = "https://www.rcrwireless.com/wp-content/uploads/2025/07/Uk-123rf-1200.jpg"

print(f"\n=== Testing Image Validation for: {test_image_url} ===\n")

try:
    # Try HEAD request first
    print("1. HEAD Request:")
    response = requests.head(test_image_url, timeout=10, allow_redirects=True)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    print(f"   Content-Length: {response.headers.get('Content-Length')}")
    
    # Try GET request
    print("\n2. GET Request:")
    response = requests.get(test_image_url, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Actual Size: {len(response.content)} bytes")
    
    # Try to open as image
    print("\n3. Image Analysis:")
    img = Image.open(BytesIO(response.content))
    print(f"   Format: {img.format}")
    print(f"   Size: {img.size}")
    print(f"   Mode: {img.mode}")
    
    # Check validation criteria
    print("\n4. Validation Checks:")
    width, height = img.size
    file_size = len(response.content)
    
    print(f"   Width >= 400? {width >= 400} ({width})")
    print(f"   Height >= 300? {height >= 300} ({height})")
    print(f"   File size >= 10KB? {file_size >= 10000} ({file_size} bytes)")
    print(f"   Valid format? {img.format in ['JPEG', 'PNG', 'WebP']}")
    
    if width >= 400 and height >= 300 and file_size >= 10000:
        print("\n✅ Image PASSES validation!")
    else:
        print("\n❌ Image FAILS validation")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
