#!/usr/bin/env python3
"""
Apply Phase 1 Performance Optimizations
Run this to make the system 5-10x faster
"""

import sqlite3
import sys

def apply_database_indexes():
    """Add database indexes for faster queries"""
    print("=" * 60)
    print("Adding Database Indexes")
    print("=" * 60)
    
    conn = sqlite3.connect('data/wireless_monitor.db')
    
    indexes = [
        ('idx_articles_score_date', 'CREATE INDEX IF NOT EXISTS idx_articles_score_date ON articles(waves_score DESC, published_date DESC)'),
        ('idx_articles_published', 'CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_date DESC)'),
        ('idx_articles_feed', 'CREATE INDEX IF NOT EXISTS idx_articles_feed ON articles(feed_id, published_date DESC)'),
        ('idx_articles_url', 'CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)'),
        ('idx_articles_source_type', 'CREATE INDEX IF NOT EXISTS idx_articles_source_type ON articles(source_type, published_date DESC)'),
        ('idx_event_articles_event', 'CREATE INDEX IF NOT EXISTS idx_event_articles_event ON event_articles(event_id, relevance_score DESC)'),
        ('idx_social_posts_account', 'CREATE INDEX IF NOT EXISTS idx_social_posts_account ON social_posts(account_id, created_at DESC)'),
        ('idx_wild_wifi_quality', 'CREATE INDEX IF NOT EXISTS idx_wild_wifi_quality ON wild_wifi_stories(quality_score DESC, featured DESC)'),
    ]
    
    for name, sql in indexes:
        try:
            conn.execute(sql)
            print(f"✅ Created index: {name}")
        except Exception as e:
            print(f"⚠️  Index {name} already exists or error: {e}")
    
    conn.commit()
    
    # Analyze database for query optimization
    print("\nAnalyzing database...")
    conn.execute('ANALYZE')
    conn.commit()
    
    conn.close()
    print("\n✅ Database indexes applied")

def optimize_database():
    """Optimize database for better performance"""
    print("\n" + "=" * 60)
    print("Optimizing Database")
    print("=" * 60)
    
    conn = sqlite3.connect('data/wireless_monitor.db')
    
    # Enable WAL mode for better concurrent access
    print("Enabling WAL mode...")
    conn.execute('PRAGMA journal_mode=WAL')
    
    # Optimize cache size
    print("Optimizing cache size...")
    conn.execute('PRAGMA cache_size=10000')
    
    # Use memory for temp storage
    print("Configuring temp storage...")
    conn.execute('PRAGMA temp_store=memory')
    
    # Optimize synchronous mode
    print("Optimizing synchronous mode...")
    conn.execute('PRAGMA synchronous=NORMAL')
    
    conn.commit()
    conn.close()
    
    print("✅ Database optimized")

def cleanup_old_data():
    """Remove old data to improve performance"""
    print("\n" + "=" * 60)
    print("Cleaning Up Old Data")
    print("=" * 60)
    
    conn = sqlite3.connect('data/wireless_monitor.db')
    
    # Count articles before
    before = conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0]
    print(f"Articles before cleanup: {before}")
    
    # Delete articles older than 90 days
    deleted = conn.execute('''
        DELETE FROM articles 
        WHERE DATE(published_date) < DATE('now', '-90 days')
    ''').rowcount
    
    print(f"Deleted {deleted} old articles (>90 days)")
    
    # Delete orphaned event articles
    orphaned = conn.execute('''
        DELETE FROM event_articles 
        WHERE article_id NOT IN (SELECT id FROM articles)
    ''').rowcount
    
    print(f"Deleted {orphaned} orphaned event articles")
    
    # Delete orphaned social shares
    orphaned_shares = conn.execute('''
        DELETE FROM social_shares 
        WHERE article_id NOT IN (SELECT id FROM articles)
    ''').rowcount
    
    print(f"Deleted {orphaned_shares} orphaned social shares")
    
    conn.commit()
    
    # Vacuum to reclaim space
    print("\nVacuuming database...")
    conn.execute('VACUUM')
    
    # Count after
    after = conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0]
    print(f"Articles after cleanup: {after}")
    
    conn.close()
    
    print("✅ Cleanup complete")

def show_database_stats():
    """Show database statistics"""
    print("\n" + "=" * 60)
    print("Database Statistics")
    print("=" * 60)
    
    conn = sqlite3.connect('data/wireless_monitor.db')
    conn.row_factory = sqlite3.Row
    
    # Article count by source
    print("\nArticles by source type:")
    sources = conn.execute('''
        SELECT source_type, COUNT(*) as count
        FROM articles
        GROUP BY source_type
        ORDER BY count DESC
    ''').fetchall()
    
    for source in sources:
        print(f"  {source['source_type'] or 'rss'}: {source['count']}")
    
    # Recent articles
    recent = conn.execute('''
        SELECT COUNT(*) as count
        FROM articles
        WHERE DATE(published_date) >= DATE('now', '-7 days')
    ''').fetchone()
    
    print(f"\nRecent articles (last 7 days): {recent['count']}")
    
    # Database size
    import os
    db_size = os.path.getsize('data/wireless_monitor.db') / 1024 / 1024
    print(f"Database size: {db_size:.2f} MB")
    
    # Score distribution
    print("\nScore distribution:")
    scores = conn.execute('''
        SELECT 
            CASE 
                WHEN waves_score >= 80 THEN 'High (80+)'
                WHEN waves_score >= 50 THEN 'Medium (50-79)'
                WHEN waves_score > 0 THEN 'Low (1-49)'
                ELSE 'Unscored (0)'
            END as category,
            COUNT(*) as count
        FROM articles
        GROUP BY category
        ORDER BY MIN(waves_score) DESC
    ''').fetchall()
    
    for score in scores:
        print(f"  {score['category']}: {score['count']}")
    
    conn.close()

def main():
    """Apply all Phase 1 optimizations"""
    print("\n" + "=" * 60)
    print("PHASE 1 PERFORMANCE OPTIMIZATIONS")
    print("=" * 60)
    print("\nThis will:")
    print("1. Add database indexes for faster queries")
    print("2. Optimize database settings")
    print("3. Clean up old data (>90 days)")
    print("4. Show database statistics")
    print("\nExpected improvement: 5-10x faster")
    print("=" * 60)
    
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted")
        return
    
    try:
        # Apply optimizations
        apply_database_indexes()
        optimize_database()
        cleanup_old_data()
        show_database_stats()
        
        print("\n" + "=" * 60)
        print("✅ PHASE 1 OPTIMIZATIONS COMPLETE")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart the application")
        print("2. Test page load speed")
        print("3. Monitor memory usage")
        print("4. Check /health endpoint")
        print("\nFor more optimizations, see PERFORMANCE_OPTIMIZATION.md")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
