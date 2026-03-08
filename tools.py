import sqlite3

# دالة لجلب الساعات المتاحة
def get_available_slots(doctor_name, date):
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        
        # الساعات المتاحة الافتراضية (ساعة لكل موعد)
        all_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        
        # جلب الساعات المحجوزة لهذا الدكتور في هذا اليوم
        cursor.execute("SELECT time FROM appointments WHERE doctor_name = ? AND date = ?", (doctor_name, date))
        booked_slots = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # تصفية الساعات المتاحة
        available = [slot for slot in all_slots if slot not in booked_slots]
        
        if not available:
            return f"للأسف، جدول الدكتور {doctor_name} ممتلئ تماماً في هذا اليوم."
        return f"الساعات المتاحة للدكتور {doctor_name} في تاريخ {date} هي: {', '.join(available)}"
    except Exception as e:
        return f"خطأ في جلب المواعيد: {str(e)}"

# تعديل دالة الحجز لتفحص التعارض
def create_appointment(patient_name, doctor_name, date, time, reason):
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()

        # التأكد من عدم وجود تعارض قبل الحجز
        cursor.execute("SELECT * FROM appointments WHERE doctor_name = ? AND date = ? AND time = ?", (doctor_name, date, time))
        if cursor.fetchone():
            conn.close()
            return f"خطأ: الوقت {time} محجوز مسبقاً لهذا الطبيب. يرجى استخدام دالة 'get_available_slots' لاقتراح وقت آخر."

        cursor.execute(
            "INSERT INTO appointments (patient_name, doctor_name, date, time, reason) VALUES (?, ?, ?, ?, ?)",
            (patient_name, doctor_name, date, time, reason)
        )
        conn.commit()
        conn.close()
        return f"تم حجز موعد {patient_name} مع {doctor_name} بنجاح في {date} الساعة {time}."
    except Exception as e:
        return f"خطأ فني: {str(e)}"

# تحديث الـ Schema ليشمل الدالتين
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "معرفة الساعات المتاحة للطبيب قبل الحجز أو عند وجود تعارض.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"}
                },
                "required": ["doctor_name", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_appointment",
            "description": "حجز موعد جديد بعد التأكد من توفر الوقت.",
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
