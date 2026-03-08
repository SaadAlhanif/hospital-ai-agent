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

# تنسيق CSS للمحادثة والعربية
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

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "أنت مساعد مستشفى ذكي. تاريخ اليوم هو 2026-03-08. ساعد المرضى بلغة عربية مؤدبة."}]

    # عرض الرسائل السابقة
    for msg in st.session_state.messages:
        if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"] and msg.get("content"):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # خانة الإدخال
    if prompt := st.chat_input("كيف يمكنني مساعدتك؟"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

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
                    args = json.loads(tool.function.arguments)
                    result = create_appointment(**args)
                    st.session_state.messages.append({"role": "tool", "tool_call_id": tool.id, "name": tool.function.name, "content": result})
                
                final_res = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.messages)
                reply = final_res.choices[0].message.content
            else:
                reply = res_msg.content

            placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun() # لتحديث الواجهة فوراً

with tab2:
    if st.text_input("كلمة المرور", type="password") == "saad2026":
        conn = sqlite3.connect("hospital.db")
        st.write("### قائمة المواعيد")
        st.dataframe(pd.read_sql_query("SELECT * FROM appointments ORDER BY id DESC", conn), use_container_width=True)
        conn.close()
