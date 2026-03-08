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

st.set_page_config(page_title="مساعد المستشفى الذكي", layout="centered", page_icon="🏥")

# --- CSS متقدم لحل مشكلة التمرير التلقائي ودفع المحادثة للأعلى ---
st.markdown("""
    <style>
    /* محاذاة النص للعربية */
    div[data-testid="stChatMessageContent"] p {
        text-align: right;
        direction: rtl;
    }
    /* جعل منطقة الرسائل تأخذ المساحة الكاملة وتدفع الإدخال للأسفل */
    .main .block-container {
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>🏥 مساعد مستشفى PSAU الذكي</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💬 حجز موعد", "🔐 الإدارة"])

with tab1:
    # 1. مرجع الأطباء (اختياري)
    with st.expander("👨‍⚕️ استعراض الأطباء المتاحين"):
        conn = sqlite3.connect("hospital.db")
        docs_df = pd.read_sql_query("SELECT name, specialty, availability FROM doctors", conn)
        st.table(docs_df)
        conn.close()

    # 2. تهيئة سجل المحادثة
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "أنت مساعد مستشفى ذكي ومؤدب. ساعد المرضى في حجز المواعيد بلغة عربية واضحة."}
        ]

    # 3. عرض الرسائل السابقة داخل حاوية مخصصة
    # هذا يضمن أن الرسائل تظهر فوق بعضها البعض بشكل مرتب
    for msg in st.session_state.messages:
        if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"] and msg.get("content"):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 4. خانة الإدخال (دائماً تظهر في أسفل الصفحة في Streamlit)
    if prompt := st.chat_input("اكتب رسالتك هنا..."):
        # عرض رسالة المستخدم فوراً
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # توليد رد الذكاء الاصطناعي
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
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
                    
                    if func_name == "create_appointment":
                        result = create_appointment(**args)
                    elif func_name == "get_available_doctors":
                        result = str(docs_df.to_dict())
                    
                    st.session_state.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": result
                    })

                final_res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages
                )
                reply = final_res.choices[0].message.content
            else:
                reply = response_message.content

            # عرض الرد النهائي
            response_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            # خدعة لإجبار الصفحة على التحديث والنزول للأسفل
            st.rerun()

with tab2:
    if st.text_input("كلمة المرور", type="password") == "saad2026":
        conn = sqlite3.connect("hospital.db")
        st.dataframe(pd.read_sql_query("SELECT * FROM appointments", conn), use_container_width=True)
        conn.close()
