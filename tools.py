import sqlite3

def get_available_doctors():
    """هذه الدالة تجلب قائمة الأطباء من قاعدة البيانات"""
    conn = sqlite3.connect("hospital.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT name, specialty, availability FROM doctors")
    doctors = cursor.fetchall()
    conn.close()
    return str(doctors)

def create_appointment(patient_name, doctor_name, date, time, reason):
    """هذه الدالة تقوم بحجز الموعد"""
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (patient_name, doctor_name, date, time, reason) VALUES (?, ?, ?, ?, ?)",
            (patient_name, doctor_name, date, time, reason)
        )
        conn.commit()
        conn.close()
        return f"تم تسجيل الموعد بنجاح للمريض {patient_name} مع {doctor_name} يوم {date} الساعة {time}."
    except Exception as e:
        return f"حدث خطأ أثناء الحجز: {str(e)}"

# هيكل الأدوات لـ OpenAI
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_available_doctors",
            "description": "استخدم هذه الدالة لمعرفة أسماء الأطباء وتخصصاتهم المتاحة في المستشفى.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": "استخدم هذه الدالة لحجز موعد طبي جديد.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "doctor_name": {"type": "string"},
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["patient_name", "doctor_name", "date", "time", "reason"]
            }
        }
    }
]
