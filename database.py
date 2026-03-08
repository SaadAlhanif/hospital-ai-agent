import sqlite3

def init_db():
    conn = sqlite3.connect("hospital.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # إنشاء جدول الأطباء
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialty TEXT,
        availability TEXT
    )
    """)

    # إنشاء جدول المواعيد
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor_name TEXT,
        date TEXT,
        time TEXT,
        reason TEXT
    )
    """)

    # إضافة أطباء تجريبيين إذا كان الجدول فارغاً
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        doctors = [
            ('د. أحمد العتيبي', 'أمراض القلب', '9 صباحاً - 5 مساءً'),
            ('د. سارة الشهري', 'طب الأطفال', '10 صباحاً - 4 مساءً'),
            ('د. خالد الدوسري', 'جراحة العظام', '1 مساءً - 8 مساءً')
        ]
        cursor.executemany("INSERT INTO doctors (name, specialty, availability) VALUES (?, ?, ?)", doctors)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
