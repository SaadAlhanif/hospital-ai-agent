def get_available_slots(doctor_name, date):
    """دالة تجلب الساعات المتاحة للطبيب في يوم محدد (بافتراض دوام 8 ساعات)"""
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        
        # الساعات الافتراضية للدوام (من 9 صباحاً إلى 5 مساءً)
        all_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        
        # جلب الساعات المحجوزة فعلياً من قاعدة البيانات لهذا الدكتور في هذا اليوم
        cursor.execute("SELECT time FROM appointments WHERE doctor_name = ? AND date = ?", (doctor_name, date))
        booked_slots = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # استخراج الساعات المتاحة (التي ليست في قائمة المحجوز)
        available = [slot for slot in all_slots if slot not in booked_slots]
        
        if not available:
            return f"للأسف، جدول الدكتور {doctor_name} ممتلئ تماماً في تاريخ {date}."
        
        return f"الساعات المتاحة للدكتور {doctor_name} يوم {date} هي: " + ", ".join(available)
    except Exception as e:
        return f"حدث خطأ أثناء فحص التوافر: {str(e)}"

# --- تحديث الـ Schema ليتمكن الـ AI من رؤية الدالة الجديدة ---
tools_schema.append({
    "type": "function",
    "function": {
        "name": "get_available_slots",
        "description": "استخدم هذه الدالة لمعرفة الساعات المتاحة للطبيب في يوم معين قبل اقتراح وقت على المريض.",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {"type": "string"},
                "date": {"type": "string", "description": "التاريخ بصيغة YYYY-MM-DD"}
            },
            "required": ["doctor_name", "date"]
        }
    }
})
