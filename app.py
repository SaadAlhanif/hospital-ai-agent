import streamlit as st
from openai import OpenAI
import json
import sqlite3
import pandas as pd
from database import init_db
from tools import create_appointment, tools_schema

# تهيئة النظام
init_db()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="مساعد مستشفى PSAU", layout="centered")

# تنسيق CSS للمحادثة والعربية وضمان بقاء الإدخال في الأسفل
st.markdown("""
    <style>
    div[data-testid="stChatMessageContent"] p { text-align: right; direction: rtl; }
    .main .block-container { display: flex; flex-direction: column; justify-content: flex-end; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 مساعد مستشفى PSAU الذكي")

tab1, tab2 = st.tabs(["💬 حجز موعد", "🔐 الإدارة"])

with tab1:
    # عرض الأطباء
    with st.expander("👨‍⚕️ استعراض الأطباء المتاحين"):
        conn = sqlite3.connect("hospital.db")
        st.table(pd.read_sql_query("SELECT name, specialty, availability FROM doctors", conn))
        conn.close()

    # تحديث تعليمات النظام ليكون العميل "Agent" أكثر ذكاءً في التعامل مع المواعيد
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "system", 
            "content": """أنت مساعد مستشفى ذكي ومحترف. تاريخ اليوم 2026-03-09. 
            عندما يطلب المريض حجزاً:
            1. استخدم دائماً دالة 'get_available_slots' أولاً لتعرض له الساعات المتاحة (ساعة لكل موعد من 9ص إلى 5م).
            2. إذا كان الوقت الذي اختاره المريض محجوزاً (يظهر لك رد 'خطأ: تعارض')، اعتذر له بلباقة واعرض عليه الساعات المتاحة المتبقية في ذلك اليوم.
            3. لا تقم بالحجز النهائي 'create_appointment' إلا بعد أن يختار المريض ساعة محددة من المواعيد المتاحة.
            4. تحدث دائماً باللغة العربية بأسلوب مهذب وودود."""
        }]

    # عرض الرسائل السابقة
    for msg in st.session_state.messages:
        if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"] and msg.get("content"):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # خانة الإدخال
    if prompt := st.chat_input("كيف يمكنني مساعدتك؟"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                tools=tools_schema
            )
            
            res_msg = response.choices[0].message
            if res_msg.tool_calls:
                st.session_state.messages.append(res_msg)
                for tool in res_msg.tool_calls:
                    func_name = tool.function.name
                    args = json.loads(tool.function.arguments)
                    
                    # منطق اختيار الدالة الصحيحة بناءً على طلب الـ AI
                    if func_name == "create_appointment":
                        result = create_appointment(**args)
                    elif func_name == "get_available_slots":
                        from tools import get_available_slots # استيراد الدالة الجديدة
                        result = get_available_slots(**args)
                    
                    st.session_state.messages.append({
                        "role": "tool", 
                        "tool_call_id": tool.id, 
                        "name": func_name, 
                        "content": result
                    })
                
                # الحصول على الرد النهائي الموجه للمستخدم بعد تنفيذ الأدوات
                final_res = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=st.session_state.messages
                )
                reply = final_res.choices[0].message.content
            else:
                reply = res_msg.content

            placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun() # تحديث الواجهة فوراً لضمان ترتيب المحادثة

with tab2:
    if st.text_input("كلمة المرور", type="password") == "saad2026":
        conn = sqlite3.connect("hospital.db")
        st.write("### قائمة المواعيد المسجلة")
        # ترتيب المواعيد من الأحدث إلى الأقدم
        st.dataframe(pd.read_sql_query("SELECT * FROM appointments ORDER BY id DESC", conn), use_container_width=True)
        conn.close()
