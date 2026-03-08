import sqlite3

def create_appointment(name, date, time, reason):
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (name, date, time, reason) VALUES (?, ?, ?, ?)",
            (name, date, time, reason)
        )
        conn.commit()
        conn.close()
        return f"تم بنجاح حجز موعد لـ {name} بتاريخ {date} الساعة {time}."
    except Exception as e:
        return f"خطأ في عملية الحجز: {str(e)}"

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": "استخدم هذه الدالة لحجز موعد طبي جديد في المستشفى.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "اسم المريض الثلاثي"},
                    "date": {"type": "string", "description": "تاريخ الموعد (YYYY-MM-DD)"},
                    "time": {"type": "string", "description": "وقت الموعد (مثلاً 10:00 AM)"},
                    "reason": {"type": "string", "description": "سبب الزيارة أو الحالة الصحية"}
                },
                "required": ["name", "date", "time", "reason"]
            }
        }
    }
]
