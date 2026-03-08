import sqlite3

def create_appointment(patient_name, doctor_name, date, time, reason):
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (patient_name, doctor_name, date, time, reason) VALUES (?, ?, ?, ?, ?)",
            (patient_name, doctor_name, date, time, reason)
        )
        conn.commit()
        conn.close()
        return f"تم تسجيل الموعد بنجاح للمريض {patient_name} مع {doctor_name} بتاريخ {date} الساعة {time}."
    except Exception as e:
        return f"خطأ في الحجز: {str(e)}"

# تعريف المهام للـ AI
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": "استخدم هذه الدالة لحجز موعد طبي جديد في قاعدة البيانات.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "doctor_name": {"type": "string"},
                    "date": {"type": "string", "description": "التاريخ بصيغة YYYY-MM-DD"},
                    "time": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["patient_name", "doctor_name", "date", "time", "reason"]
            }
        }
    }
]
