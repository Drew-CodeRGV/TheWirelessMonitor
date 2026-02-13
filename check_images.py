import sqlite3

conn = sqlite3.connect('data/wireless_monitor.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT id, title, url, image_url 
    FROM articles 
    ORDER BY id DESC 
    LIMIT 15
''')

rows = cursor.fetchall()

print("\n=== Recent Articles and Their Images ===\n")
for row in rows:
    article_id, title, url, image_url = row
    print(f"ID: {article_id}")
    print(f"Title: {title[:70]}...")
    print(f"URL: {url}")
    print(f"Image: {image_url[:100] if image_url else 'NONE'}...")
    print("-" * 80)

conn.close()
