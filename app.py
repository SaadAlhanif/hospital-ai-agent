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

# --- تنسيق الواجهة ---
st.markdown("""
    <style>
    div[data-testid="stChatMessageContent"] p {
        text-align: right;
        direction: rtl;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>🏥 مساعد مستشفى PSAU الذكي</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💬 حجز موعد", "🔐 الإدارة"])

with tab1:
    # عرض الأطباء
    with st.expander("👨‍⚕️ استعراض الأطباء المتاحين"):
        conn = sqlite3.connect("hospital.db")
        docs = pd.read_sql_query("SELECT name, specialty, availability FROM doctors", conn)
        st.table(docs)
        conn.close()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "أنت مساعد مستشفى ذكي ومؤدب. ساعد المرضى في حجز المواعيد."}
        ]

    # عرض الرسائل (تم إصلاح هذا الجزء لتجنب الخطأ)
    for msg in st.session_state.messages:
        # التأكد أن الرسالة تحتوي على محتوى نصي ولها دور مستخدم أو مساعد
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            if msg["role"] in ["user", "assistant"] and msg["content"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    if prompt := st.chat_input("كيف يمكنني مساعدتك؟"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

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
                        result = str(docs.to_dict())
                    
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

            response_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

with tab2:
    if st.text_input("كلمة المرور", type="password") == "saad2026":
        conn = sqlite3.connect("hospital.db")
        st.dataframe(pd.read_sql_query("SELECT * FROM appointments", conn))
        conn.close()
