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
        return f"تم تسجيل الموعد بنجاح للمريض {patient_name} مع {doctor_name} يوم {date} الساعة {time}."
    except Exception as e:
        return f"حدث خطأ أثناء الحجز: {str(e)}"

# هذا الهيكل يخبر OpenAI كيف يستخدم الدوال
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": "استخدم هذه الدالة لحجز موعد طبي جديد.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string", "description": "اسم المريض الثنائي أو الثلاثي"},
                    "doctor_name": {"type": "string", "description": "اسم الطبيب المختار"},
                    "date": {"type": "string", "description": "التاريخ بصيغة YYYY-MM-DD"},
                    "time": {"type": "string", "description": "الوقت المطلوب"},
                    "reason": {"type": "string", "description": "سبب الزيارة"}
                },
                "required": ["patient_name", "doctor_name", "date", "time", "reason"]
            }
        }
    }
]
