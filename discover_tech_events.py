#!/usr/bin/env python3
"""
Discover tech industry events with CFP tracking
Searches for wireless, hospitality tech, restaurant tech, retail tech events
"""

import sqlite3
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time

# Event search queries
EVENT_QUERIES = [
    "WiFi conference 2026",
    "wireless technology conference 2026",
    "5G summit 2026",
    "hospitality technology conference 2026",
    "restaurant technology conference 2026",
    "retail technology conference 2026",
    "IoT conference 2026",
    "networking conference 2026",
    "telecommunications conference 2026",
    "mobile world congress 2026"
]

CFP_QUERIES = [
    "call for papers wireless 2026",
    "call for speakers technology conference 2026",
    "CFP networking conference 2026",
    "submit talk proposal tech conference 2026"
]

# Known major events (manually curated)
KNOWN_EVENTS = [
    {
        'name': 'Mobile World Congress 2026',
        'start_date': '2026-03-02',
        'end_date': '2026-03-05',
        'location': 'Barcelona, Spain',
        'description': 'The world\'s largest mobile industry event',
        'hashtags': '#MWC26,#MWC2026',
        'cfp_status': 'closed',
        'website': 'https://www.mwcbarcelona.com'
    },
    {
        'name': 'CES 2026',
        'start_date': '2026-01-06',
        'end_date': '2026-01-09',
        'location': 'Las Vegas, NV',
        'description': 'Consumer Electronics Show - latest tech innovations',
        'hashtags': '#CES2026',
        'cfp_status': 'unknown',
        'website': 'https://www.ces.tech'
    },
    {
        'name': 'HITEC 2026',
        'start_date': '2026-06-15',
        'end_date': '2026-06-18',
        'location': 'TBD',
        'description': 'Hospitality Industry Technology Exposition and Conference',
        'hashtags': '#HITEC2026',
        'cfp_status': 'open',
        'website': 'https://www.hitec.org'
    },
    {
        'name': 'NRF 2026',
        'start_date': '2026-01-12',
        'end_date': '2026-01-14',
        'location': 'New York, NY',
        'description': 'National Retail Federation - Retail\'s Big Show',
        'hashtags': '#NRF2026',
        'cfp_status': 'unknown',
        'website': 'https://nrf.com'
    },
    {
        'name': 'Interop 2026',
        'start_date': '2026-05-18',
        'end_date': '2026-05-22',
        'location': 'Las Vegas, NV',
        'description': 'Enterprise networking and infrastructure conference',
        'hashtags': '#Interop2026',
        'cfp_status': 'unknown',
        'website': 'https://www.interop.com'
    }
]

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('data/wireless_monitor.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_or_update_event(conn, event):
    """Add or update an event in the database"""
    try:
        # Check if event exists
        existing = conn.execute(
            'SELECT id FROM industry_events WHERE name = ?',
            (event['name'],)
        ).fetchone()
        
        if existing:
            # Update existing event
            conn.execute('''
                UPDATE industry_events 
                SET start_date = ?, end_date = ?, location = ?, 
                    description = ?, hashtags = ?, active = 1,
                    cfp_status = ?, website = ?
                WHERE id = ?
            ''', (
                event['start_date'], event['end_date'], event['location'],
                event['description'], event['hashtags'], 
                event.get('cfp_status', 'unknown'),
                event.get('website', ''),
                existing['id']
            ))
            print(f"✅ Updated: {event['name']}")
            return existing['id']
        else:
            # Insert new event
            cursor = conn.execute('''
                INSERT INTO industry_events 
                (name, start_date, end_date, location, description, hashtags, active, cfp_status, website)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            ''', (
                event['name'], event['start_date'], event['end_date'],
                event['location'], event['description'], event['hashtags'],
                event.get('cfp_status', 'unknown'),
                event.get('website', '')
            ))
            print(f"✅ Added: {event['name']}")
            return cursor.lastrowid
            
    except Exception as e:
        print(f"❌ Error adding event {event['name']}: {e}")
        return None

def check_cfp_status(event_name, website):
    """Check if an event has an open CFP"""
    try:
        if not website:
            return 'unknown'
        
        # Try to fetch the event website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(website, headers=headers, timeout=10)
        
        if response.status_code == 200:
            text = response.text.lower()
            
            # Check for CFP indicators
            cfp_indicators = [
                'call for papers', 'call for speakers', 'submit a proposal',
                'speaker submission', 'cfp', 'submit talk', 'call for presentations'
            ]
            
            closed_indicators = [
                'cfp closed', 'submissions closed', 'deadline passed'
            ]
            
            if any(indicator in text for indicator in closed_indicators):
                return 'closed'
            elif any(indicator in text for indicator in cfp_indicators):
                return 'open'
        
        return 'unknown'
        
    except Exception as e:
        print(f"  ⚠️  Could not check CFP status: {e}")
        return 'unknown'

def main():
    print("=" * 60)
    print("TECH EVENT DISCOVERY")
    print("=" * 60)
    print()
    
    conn = get_db_connection()
    
    # Add known major events
    print("Adding known major events...")
    print("-" * 60)
    
    for event in KNOWN_EVENTS:
        # Check CFP status if website provided
        if event.get('website'):
            print(f"Checking CFP status for {event['name']}...")
            cfp_status = check_cfp_status(event['name'], event['website'])
            event['cfp_status'] = cfp_status
            print(f"  CFP Status: {cfp_status}")
        
        add_or_update_event(conn, event)
        time.sleep(1)  # Be nice to servers
    
    conn.commit()
    
    # Show summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_events = conn.execute('SELECT COUNT(*) FROM industry_events WHERE active = 1').fetchone()[0]
    cfp_open = conn.execute('SELECT COUNT(*) FROM industry_events WHERE cfp_status = "open"').fetchone()[0]
    
    print(f"Total active events: {total_events}")
    print(f"Events with open CFP: {cfp_open}")
    
    # Show events with open CFP
    if cfp_open > 0:
        print()
        print("Events currently accepting speakers:")
        print("-" * 60)
        cfp_events = conn.execute('''
            SELECT name, start_date, location, website 
            FROM industry_events 
            WHERE cfp_status = "open" AND active = 1
            ORDER BY start_date
        ''').fetchall()
        
        for event in cfp_events:
            print(f"📢 {event['name']}")
            print(f"   Date: {event['start_date']}")
            print(f"   Location: {event['location']}")
            print(f"   Website: {event['website']}")
            print()
    
    conn.close()
    print()
    print("✅ Event discovery complete!")

if __name__ == '__main__':
    main()
