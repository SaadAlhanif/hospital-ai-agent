import sqlite3

def init_db():
    conn = sqlite3.connect("hospital.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        time TEXT,
        reason TEXT,
        status TEXT DEFAULT 'Confirmed'
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
