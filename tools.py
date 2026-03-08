import sqlite3

def get_available_slots(doctor_name, date):
    """جلب الساعات المتاحة بناءً على جدول الطبيب في قاعدة البيانات"""
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        
        # جلب ساعات عمل الطبيب الفعلية
        cursor.execute("SELECT availability FROM doctors WHERE name = ?", (doctor_name,))
        row = cursor.fetchone()
        
        if not row:
            return f"لم يتم العثور على الطبيب {doctor_name}."
        
        avail_text = row[0]
        
        # تحديد الساعات بناءً على النص الموجود في قاعدة البيانات
        if "1" in avail_text and "8" in avail_text:
            all_slots = ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
        elif "9" in avail_text and "5" in avail_text:
            all_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        elif "10" in avail_text and "4" in avail_text:
            all_slots = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        else:
            all_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]

        # جلب المواعيد المحجوزة
        cursor.execute("SELECT time FROM appointments WHERE doctor_name = ? AND date = ?", (doctor_name, date))
        booked = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        available = [s for s in all_slots if s not in booked]
        return f"الساعات المتاحة للدكتور {doctor_name} في {date} هي: " + ", ".join(available)
    except Exception as e:
        return f"خطأ: {str(e)}"

def create_appointment(patient_name, doctor_name, date, time, reason):
    """حجز الموعد بعد التأكد من عدم وجود تعارض"""
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        
        # التأكد من عدم وجود تعارض
        cursor.execute("SELECT id FROM appointments WHERE doctor_name = ? AND date = ? AND time = ?", 
                       (doctor_name, date, time))
        if cursor.fetchone():
            conn.close()
            return f"خطأ: الوقت {time} محجوز مسبقاً. يرجى مراجعة المواعيد المتاحة."

        cursor.execute(
            "INSERT INTO appointments (patient_name, doctor_name, date, time, reason) VALUES (?, ?, ?, ?, ?)",
            (patient_name, doctor_name, date, time, reason)
        )
        conn.commit()
        conn.close()
        return f"تم حجز موعد {patient_name} مع {doctor_name} بنجاح في {date} الساعة {time}."
    except Exception as e:
        return f"خطأ فني: {str(e)}"

# تعريف الـ Schema لـ OpenAI
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "معرفة الساعات المتاحة للطبيب في يوم محدد.",
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
            "description": "حجز موعد طبي جديد.",
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
