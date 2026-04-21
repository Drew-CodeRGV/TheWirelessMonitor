#!/usr/bin/env python3
"""Add CFP tracking columns to events table"""

import sqlite3

def main():
    conn = sqlite3.connect('data/wireless_monitor.db')
    
    try:
        # Add cfp_status column
        conn.execute('ALTER TABLE industry_events ADD COLUMN cfp_status TEXT DEFAULT "unknown"')
        print("✅ Added cfp_status column")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("⚠️  cfp_status column already exists")
        else:
            raise
    
    try:
        # Add website column
        conn.execute('ALTER TABLE industry_events ADD COLUMN website TEXT')
        print("✅ Added website column")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("⚠️  website column already exists")
        else:
            raise
    
    conn.commit()
    conn.close()
    print("✅ Migration complete!")

if __name__ == '__main__':
    main()
