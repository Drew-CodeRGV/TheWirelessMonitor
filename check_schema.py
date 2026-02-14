import sqlite3

conn = sqlite3.connect('data/wireless_monitor.db')
cursor = conn.cursor()

# Get articles table schema
cursor.execute("SELECT sql FROM sqlite_master WHERE name='articles'")
print(cursor.fetchone()[0])

conn.close()
