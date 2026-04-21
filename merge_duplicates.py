#!/usr/bin/env python3
"""
Merge existing duplicate articles in the database
This will increase cross_source_count for articles covered by multiple sources
"""

import sys
import sqlite3
from difflib import SequenceMatcher

sys.path.insert(0, '.')

def clean_title_for_matching(title: str) -> str:
    """Clean title for duplicate detection"""
    title = title.lower().strip()
    
    # Remove common prefixes
    prefixes = ['breaking:', 'exclusive:', 'report:', 'analysis:', 'opinion:', 
                'video:', 'live:', 'update:', 'watch:', 'read:']
    for prefix in prefixes:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
    
    # Remove source attributions at end
    for sep in [' - ', ' | ', ' :: ', ' — ']:
        if sep in title:
            parts = title.split(sep)
            # Keep the first part (actual title)
            title = parts[0].strip()
    
    return title

def merge_duplicates():
    """Find and merge duplicate articles"""
    print("=" * 60)
    print("Merging Duplicate Articles")
    print("=" * 60)
    
    conn = sqlite3.connect('data/wireless_monitor.db')
    conn.row_factory = sqlite3.Row
    
    # Get all articles
    articles = conn.execute('''
        SELECT id, title, url, cross_source_count
        FROM articles
        ORDER BY id
    ''').fetchall()
    
    print(f"\nChecking {len(articles)} articles for duplicates...\n")
    
    merged_count = 0
    processed = set()
    
    for i, article1 in enumerate(articles):
        if article1['id'] in processed:
            continue
        
        duplicates = []
        
        for article2 in articles[i+1:]:
            if article2['id'] in processed:
                continue
            
            # Check exact URL match
            if article1['url'] == article2['url']:
                duplicates.append(article2)
                continue
            
            # Check title similarity
            title1 = clean_title_for_matching(article1['title'])
            title2 = clean_title_for_matching(article2['title'])
            
            # Calculate similarity
            similarity = SequenceMatcher(None, title1, title2).ratio()
            
            # Check if one title contains the other (substring match)
            if title1 in title2 or title2 in title1:
                similarity = max(similarity, 0.85)
            
            if similarity >= 0.80:
                duplicates.append(article2)
        
        if duplicates:
            # Keep the first article, merge others into it
            new_count = article1['cross_source_count'] + len(duplicates)
            
            print(f"Merging {len(duplicates)} duplicates into article {article1['id']}:")
            print(f"  Title: {article1['title'][:70]}")
            print(f"  New cross_source_count: {new_count}")
            
            # Update the kept article
            conn.execute('''
                UPDATE articles 
                SET cross_source_count = ?
                WHERE id = ?
            ''', (new_count, article1['id']))
            
            # Delete the duplicates
            for dup in duplicates:
                print(f"    - Removing duplicate ID {dup['id']}")
                conn.execute('DELETE FROM articles WHERE id = ?', (dup['id'],))
                processed.add(dup['id'])
            
            merged_count += len(duplicates)
            print()
    
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print(f"✅ Merged {merged_count} duplicate articles")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python recalculate_scores.py")
    print("2. Check the new score distribution")

if __name__ == '__main__':
    merge_duplicates()
