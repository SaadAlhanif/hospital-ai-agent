import sqlite3

conn = sqlite3.connect("clinic.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
date TEXT,
time TEXT,
reason TEXT
)
""")

conn.commit()
