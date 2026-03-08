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

# --- تنسيق الواجهة لضمان ظهور النصوص من اليمين ---
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
    # عرض الأطباء في الأعلى كمرجع ثابت
    with st.expander("👨‍⚕️ استعراض الأطباء المتاحين"):
        conn = sqlite3.connect("hospital.db")
        docs_df = pd.read_sql_query("SELECT name, specialty, availability FROM doctors", conn)
        st.table(docs_df)
        conn.close()

    # تهيئة السجل إذا لم يكن موجوداً
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "أنت مساعد مستشفى ذكي ومؤدب. ساعد المرضى في حجز المواعيد بلغة عربية واضحة."}
        ]

    # --- عرض الرسائل بترتيب صحيح (الأقدم فوق والأحدث تحت) ---
    # هذا الجزء يضمن بقاء المحادثة تحت بعضها البعض
    for msg in st.session_state.messages:
        # حل مشكلة TypeError: نتأكد أن الرسالة نصية ولها دور محدد
        if isinstance(msg, dict) and msg.get("content") and msg.get("role") in ["user", "assistant"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # --- خانة الإدخال ثابتة في الأسفل تلقائياً ---
    if prompt := st.chat_input("كيف يمكنني مساعدتك اليوم؟"):
        # 1. إضافة رسالة المستخدم للسجل وعرضها فوراً في الأسفل
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. توليد رد المساعد
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                tools=tools_schema
            )
            
            response_message = response.choices[0].message
            
            # معالجة استدعاء الأدوات إذا لزم الأمر
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

                # الحصول على الرد النهائي بعد تنفيذ المهمة
                final_res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages
                )
                reply = final_res.choices[0].message.content
            else:
                reply = response_message.content

            # عرض الرد في آخر المحادثة وتخزينه
            response_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

with tab2:
    if st.text_input("كلمة المرور", type="password") == "saad2026":
        conn = sqlite3.connect("hospital.db")
        st.write("### قائمة المواعيد")
        st.dataframe(pd.read_sql_query("SELECT * FROM appointments", conn), use_container_width=True)
        conn.close()
