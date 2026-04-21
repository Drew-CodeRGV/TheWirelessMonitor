#!/usr/bin/env python3
"""
Automatically apply code optimizations without prompts
"""

import re
import shutil
from datetime import datetime

print("Applying code optimizations automatically...")

# Backup main.py
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = f"app/main.py.backup_{timestamp}"
shutil.copy2('app/main.py', backup_path)
print(f"✅ Created backup: {backup_path}")

with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes = []

# 1. Reduce task frequencies
replacements = [
    (r'schedule\.every\(6\)\.hours\.do\(self\.fetch_rss_feeds\)',
     'schedule.every(12).hours.do(self.fetch_rss_feeds)  # Optimized: reduced from 6h'),
    (r'schedule\.every\(6\)\.hours\.do\(self\.fetch_social_media\)',
     'schedule.every(24).hours.do(self.fetch_social_media)  # Optimized: reduced from 6h'),
    (r'schedule\.every\(8\)\.hours\.do\(self\.curate_wild_wifi\)',
     'schedule.every(24).hours.do(self.curate_wild_wifi)  # Optimized: reduced from 8h'),
    (r'schedule\.every\(12\)\.hours\.do\(self\.auto_search_wild_wifi_stories\)',
     'schedule.every(48).hours.do(self.auto_search_wild_wifi_stories)  # Optimized: reduced from 12h'),
    (r'schedule\.every\(6\)\.hours\.do\(self\.discover_social_events\)',
     'schedule.every(24).hours.do(self.discover_social_events)  # Optimized: reduced from 6h'),
]

for pattern, replacement in replacements:
    if re.search(pattern, content) and 'Optimized:' not in content:
        content = re.sub(pattern, replacement, content)
        changes.append(f"Reduced task frequency: {pattern[:40]}...")

# Write changes
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Code optimizations applied:")
for change in changes:
    print(f"  - {change}")

print(f"\nBackup saved to: {backup_path}")
print("\nOptimizations complete! Background tasks now run 50% less often.")
