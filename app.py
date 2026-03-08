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

st.set_page_config(page_title="واتساب المستشفى الذكي", layout="wide", page_icon="🟢")

# --- 2. إضافة تنسيق WhatsApp عبر CSS ---
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        max-width: 80%;
    }
    /* رسائل المستخدم (جهة اليمين باللون الأخضر فاتح) */
    [data-testid="stChatMessageUser"] {
        background-color: #dcf8c6 !important;
        margin-left: auto;
        border: 1px solid #c7e5b4;
    }
    /* رسائل البوت (جهة اليسار باللون الأبيض) */
    [data-testid="stChatMessageAssistant"] {
        background-color: #ffffff !important;
        margin-right: auto;
        border: 1px solid #e6e6e6;
    }
    /* تحسين شكل التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #075e54;
        color: white;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. العناوين
st.markdown("<h2 style='text-align: center; color: #075e54;'>🟢 WhatsApp Hospital Assistant</h2>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💬 المحادثة (WhatsApp)", "🔐 لوحة الإدارة"])

with tab1:
    # عرض الأطباء بشكل أنيق في الأعلى
    st.markdown("<h5 style='text-align: right;'>👨‍⚕️ الأطباء المتاحون الآن:</h5>", unsafe_allow_html=True)
    conn = sqlite3.connect("hospital.db")
    doctors_df = pd.read_sql_query("SELECT name, specialty FROM doctors", conn)
    conn.close()
    
    # عرض سريع للأطباء في سطر واحد
    doc_list = " | ".join([f"**{row['name']}** ({row['specialty']})" for i, row in doctors_df.iterrows()])
    st.write(doc_list)
    st.divider()

    # --- منطق الدردشة ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "أنت مساعد مستشفى ذكي تعمل عبر واتساب. ساعد المرضى بلغة عربية ودودة ومختصرة مثل رسائل الجوال."}
        ]

    # عرض تاريخ المحادثة بتنسيق الفقاعات
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("اكتب رسالتك هنا...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Agent Logic
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
                    result = str(doctors_df.to_dict())
                
                st.session_state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result
                })

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
    st.markdown("<h3 style='text-align: right;'>دخول المسؤول</h3>", unsafe_allow_html=True)
    pwd = st.text_input("كلمة المرور", type="password")
    if pwd == "saad2026":
        conn = sqlite3.connect("hospital.db")
        st.dataframe(pd.read_sql_query("SELECT * FROM appointments", conn), use_container_width=True)
        conn.close()
