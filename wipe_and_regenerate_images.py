#!/usr/bin/env python3
"""
Wipe Image Database and Regenerate with Ultra-Aggressive Scraping
This script will:
1. Clear all existing image URLs from the database
2. Delete all generated image files
3. Force regeneration of images using the new ultra-aggressive scraping procedure
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path

# Add the app directory to the path so we can import the WirelessMonitor class
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def wipe_image_database():
    """Wipe all image URLs from the database"""
    print("🗑️  Wiping image database...")
    
    db_path = 'app/data/wireless_monitor.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    
    # Clear all image URLs from articles
    result = conn.execute('UPDATE articles SET image_url = NULL WHERE image_url IS NOT NULL')
    cleared_count = result.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"✅ Cleared {cleared_count} image URLs from database")
    return True

def delete_generated_images():
    """Delete all generated image files"""
    print("🗑️  Deleting generated image files...")
    
    image_dirs = [
        'static/generated_images',
        'app/static/generated_images'
    ]
    
    deleted_count = 0
    for image_dir in image_dirs:
        if os.path.exists(image_dir):
            for file in os.listdir(image_dir):
                if file.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    file_path = os.path.join(image_dir, file)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        print(f"⚠️  Could not delete {file_path}: {e}")
    
    print(f"✅ Deleted {deleted_count} generated image files")

def regenerate_images_with_scraping():
    """Regenerate images for all articles using ultra-aggressive scraping"""
    print("🔍 Starting ultra-aggressive image scraping for all articles...")
    
    # Import the WirelessMonitor class
    try:
        from main import WirelessMonitor
    except ImportError:
        print("❌ Could not import WirelessMonitor class")
        return False
    
    # Create monitor instance
    monitor = WirelessMonitor()
    
    # Get database connection
    conn = monitor.get_db_connection()
    
    # Get all articles to regenerate (process all articles, not just those without images)
    articles = conn.execute('''
        SELECT id, title, description, url, feed_id 
        FROM articles 
        ORDER BY published_date DESC
        LIMIT 100
    ''').fetchall()
    
    print(f"📰 Found {len(articles)} articles to process")
    
    if len(articles) == 0:
        print("ℹ️  No articles found to process")
        conn.close()
        return True
    
    success_count = 0
    failed_count = 0
    
    for i, article_row in enumerate(articles, 1):
        article_dict = dict(article_row)
        
        print(f"🔍 [{i}/{len(articles)}] Scraping: {article_dict['title'][:60]}...")
        
        try:
            # Use the ultra-aggressive scraping function
            image_url = monitor.get_or_create_article_image_sync(article_dict, conn)
            
            if image_url:
                # Update the database with the scraped image
                conn.execute('UPDATE articles SET image_url = ? WHERE id = ?', 
                           (image_url, article_dict['id']))
                conn.commit()
                success_count += 1
                print(f"✅ Success: {image_url}")
            else:
                failed_count += 1
                print(f"❌ No image found")
                
        except Exception as e:
            failed_count += 1
            print(f"❌ Error: {e}")
    
    conn.close()
    
    print(f"\n📊 Scraping Results:")
    print(f"✅ Successfully scraped: {success_count}")
    print(f"❌ Failed to find images: {failed_count}")
    
    if len(articles) > 0:
        print(f"📈 Success rate: {(success_count / len(articles) * 100):.1f}%")
    else:
        print(f"📈 Success rate: 0.0%")
    
    return True

def main():
    """Main function to orchestrate the image regeneration process"""
    print("🚀 Starting Image Database Wipe and Regeneration")
    print("=" * 60)
    
    # Step 1: Wipe the image database
    if not wipe_image_database():
        print("❌ Failed to wipe image database")
        return
    
    # Step 2: Delete generated image files
    delete_generated_images()
    
    # Step 3: Regenerate images with ultra-aggressive scraping
    print("\n" + "=" * 60)
    if not regenerate_images_with_scraping():
        print("❌ Failed to regenerate images")
        return
    
    print("\n" + "=" * 60)
    print("🎉 Image regeneration completed!")
    print("🔍 All articles now use ultra-aggressive scraping for images")

if __name__ == "__main__":
    main()