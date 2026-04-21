#!/usr/bin/env python3
"""
Test if the app can start without errors
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.path.insert(0, '.')

print("Testing app startup...")
print("=" * 60)

try:
    print("1. Importing WirelessMonitor...")
    from app.main import WirelessMonitor
    print("   [OK] Import successful")
    
    print("\n2. Initializing app...")
    monitor = WirelessMonitor()
    print("   [OK] Initialization successful")
    
    print("\n3. Testing database connection...")
    conn = monitor.get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0]
    conn.close()
    print(f"   [OK] Database OK ({count} articles)")
    
    print("\n4. Testing scoring function...")
    conn = monitor.get_db_connection()
    article = conn.execute('SELECT id FROM articles LIMIT 1').fetchone()
    if article:
        score = monitor.calculate_waves_score(article['id'], conn)
        print(f"   [OK] Scoring OK (test score: {score:.1f})")
    else:
        print("   [WARN] No articles to test scoring")
    conn.close()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - App is ready to run!")
    print("=" * 60)
    print("\nStart the app with:")
    print("  python run_local.py")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
