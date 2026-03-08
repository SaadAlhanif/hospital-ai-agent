import streamlit as st
from openai import OpenAI
import json
import sqlite3
import pandas as pd
from database import init_db
from tools import create_appointment, get_available_doctors, tools_schema

# 1. إعدادات النظام
init_db()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# إعداد الصفحة لتكون من اليمين لليسار (RTL)
st.set_page_config(page_title="مساعد المستشفى الذكي", layout="wide", page_icon="🏥")

# 4. واجهة المستخدم
st.markdown("<h1 style='text-align: right;'>🏥 نظام مساعد المستشفى الذكي</h1>", unsafe_allow_html=True)

# تقسيم الصفحة إلى تبويبات (بوابة المريض ولوحة الإدارة)
tab1, tab2 = st.tabs(["💬 بوابة المريض", "🔐 لوحة الإدارة"])

with tab1:
    # --- عرض الأطباء بشكل افتراضي ---
    st.markdown("<h3 style='text-align: right;'>👨‍⚕️ طاقمنا الطبي المتميز</h3>", unsafe_allow_html=True)
    
    conn = sqlite3.connect("hospital.db")
    doctors_df = pd.read_sql_query("SELECT name, specialty, availability FROM doctors", conn)
    conn.close()

    # عرض الأطباء في أعمدة
    cols = st.columns(len(doctors_df))
    for i, row in doctors_df.iterrows():
        with cols[i]:
            st.info(f"**{row['name']}**")
            st.write(f"التخصص: {row['specialty']}")
            st.caption(f"ساعات العمل: {row['availability']}")
    
    st.divider()
    
    # --- واجهة المحادثة ---
    st.markdown("<h3 style='text-align: right;'>تحدث مع المساعد الذكي لحجز موعد</h3>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "أنت مساعد ذكي في مستشفى. ساعد المرضى في حجز المواعيد مع الأطباء المذكورين أعلاه. تحدث باللغة العربية بأسلوب مهذب."}
        ]

    # عرض تاريخ المحادثة
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("كيف يمكنني مساعدتك اليوم؟ (مثلاً: أريد حجز موعد مع دكتور أحمد)")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # منطق العميل الذكي (Agent Logic)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            tools=tools_schema
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            st.session_state.messages.append(response_message)
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # تنفيذ المهام
                if func_name == "create_appointment":
                    # تعديل بسيط لضمان تمرير الأسماء الصحيحة للدالة باللغة العربية
                    result = create_appointment(
                        patient_name=args.get("patient_name"),
                        doctor_name=args.get("doctor_name"),
                        date=args.get("date"),
                        time=args.get("time"),
                        reason=args.get("reason")
                    )
                elif func_name == "get_available_doctors":
                    result = str(doctors_df.to_dict())
                
                st.session_state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result
                })

            # الرد النهائي من الذكاء الاصطناعي
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages
            )
            reply = final_response.choices[0].message.content
        else:
            reply = response_message.content

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.write(reply)

with tab2:
    st.markdown("<h2 style='text-align: right;'>دخول الإدارة</h2>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل كلمة مرور المسؤول", type="password")
    if pwd == "saad2026":
        conn = sqlite3.connect("hospital.db")
        st.subheader("📅 قائمة جميع المواعيد")
        df_appointments = pd.read_sql_query("SELECT * FROM appointments", conn)
        # تغيير أسماء الأعمدة للعربية في العرض فقط
        df_appointments.columns = ["المعرف", "اسم المريض", "اسم الدكتور", "التاريخ", "الوقت", "السبب"]
        st.dataframe(df_appointments, use_container_width=True)
        conn.close()
    else:
        st.warning("هذا القسم مخصص للمسؤولين فقط.")
