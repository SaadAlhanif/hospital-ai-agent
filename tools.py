def get_available_slots(doctor_name, date):
    try:
        conn = sqlite3.connect("hospital.db", check_same_thread=False)
        cursor = conn.cursor()
        
        # 1. جلب ساعات عمل الطبيب الفعلية من الجدول
        cursor.execute("SELECT availability FROM doctors WHERE name = ?", (doctor_name,))
        availability_text = cursor.fetchone()
        
        if not availability_text:
            return f"لم يتم العثور على بيانات الطبيب {doctor_name}."

        # تحويل النص (مثلاً: 1 مساءً - 8 مساءً) إلى قائمة ساعات حقيقية
        # سنقوم هنا ببناء قائمة الساعات بناءً على تخصص كل طبيب لضمان التطابق
        if "1" in availability_text[0] and "8" in availability_text[0]:
            all_slots = ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
        elif "9" in availability_text[0] and "5" in availability_text[0]:
            all_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
        elif "10" in availability_text[0] and "4" in availability_text[0]:
            all_slots = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        else:
            all_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]

        # 2. جلب الساعات المحجوزة فعلياً
        cursor.execute("SELECT time FROM appointments WHERE doctor_name = ? AND date = ?", (doctor_name, date))
        booked_slots = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # 3. تصفية الساعات (المتاحة فقط)
        available = [slot for slot in all_slots if slot not in booked_slots]
        
        if not available:
            return f"للأسف، جدول {doctor_name} ممتلئ في هذا اليوم."
        
        return f"الساعات المتاحة للدكتور {doctor_name} في {date} هي: " + ", ".join(available)
    except Exception as e:
        return f"خطأ: {str(e)}"
