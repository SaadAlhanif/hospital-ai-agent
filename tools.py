import sqlite3

def get_available_slots(doctor_name, date):
    """جلب الساعات المتاحة بناءً على جدول الطبيب الحقيقي في قاعدة البيانات"""
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        
        # البحث عن الطبيب باستخدام LIKE لتفادي مشاكل المسافات أو الأخطاء الإملائية البسيطة
        cursor.execute("SELECT name, availability FROM doctors WHERE name LIKE ?", (f"%{doctor_name}%",))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return f"عذراً، لم أجد طبيب بهذا الاسم '{doctor_name}' في النظام. يرجى التأكد من الاسم من الجدول أعلاه."
        
        real_doctor_name = row[0]
        avail_text = row[1]
        
        # تحديد قائمة الساعات بناءً على النص الموجود في عمود availability
        # د. خالد الدوسري (1 مساءً - 8 مساءً)
        if "1" in avail_text and "8" in avail_text:
            all_slots = ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
        # د. أحمد العتيبي (9 صباحاً - 5 مساءً)
        elif "9" in avail_text and "5" in avail_text:
            all_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        # د. سارة الشهري (10 صباحاً - 4 مساءً)
        elif "10" in avail_text and "4" in avail_text:
            all_slots = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        else:
            all_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00"]

        # جلب المواعيد المحجوزة فعلياً لهذا الدكتور في هذا اليوم
        cursor.execute("SELECT time FROM appointments WHERE doctor_name = ? AND date = ?", (real_doctor_name, date))
        booked = [r[0] for r in cursor.fetchall()]
        conn.close()
        
        available = [s for s in all_slots if s not in booked]
        
        if not available:
            return f"للأسف، جدول {real_doctor_name} ممتلئ تماماً في تاريخ {date}."
            
        return f"الساعات المتاحة للدكتور {real_doctor_name} في {date} هي: " + ", ".join(available)
    except Exception as e:
        return f"خطأ تقني: {str(e)}"

def create_appointment(patient_name, doctor_name, date, time, reason):
    """حجز الموعد مع التأكد من اسم الدكتور الصحيح"""
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        
        # التأكد من اسم الدكتور الصحيح من القاعدة
        cursor.execute("SELECT name FROM doctors WHERE name LIKE ?", (f"%{doctor_name}%",))
        res = cursor.fetchone()
        if not res:
            return f"خطأ: الطبيب '{doctor_name}' غير موجود."
        
        real_name = res[0]

        # فحص التعارض
        cursor.execute("SELECT id FROM appointments WHERE doctor_name = ? AND date = ? AND time = ?", (real_name, date, time))
        if cursor.fetchone():
            conn.close()
            return f"الوقت {time} محجوز مسبقاً لدى {real_name}."

        cursor.execute(
            "INSERT INTO appointments (patient_name, doctor_name, date, time, reason) VALUES (?, ?, ?, ?, ?)",
            (patient_name, real_name, date, time, reason)
        )
        conn.commit()
        conn.close()
        return f"تم الحجز بنجاح للمريض {patient_name} مع {real_name} في {date} الساعة {time}."
    except Exception as e:
        return f"فشل الحجز: {str(e)}"

# Schema
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
                    "date": {"type": "string"}
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
