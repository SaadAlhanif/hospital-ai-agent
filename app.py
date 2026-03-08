import streamlit as st
from openai import OpenAI
import json
import sqlite3
import pandas as pd
from database import init_db
from tools import create_appointment, get_available_doctors, tools_schema

# 1. إعدادات النظام الأساسية
init_db()
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="مساعد المستشفى الذكي", layout="centered", page_icon="🏥")

# --- تنسيق الواجهة لتكون محادثة احترافية ---
st.markdown("""
    <style>
    /* تنسيق الحاوية الرئيسية للمحادثة */
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    /* محاذاة النصوص للعربية */
    div[data-testid="stChatMessageContent"] p {
        text-align: right;
        direction: rtl;
    }
    /* إخفاء القوائم غير الضرورية لزيادة التركيز */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# العنوان العلوي
st.markdown("<h2 style='text-align: center;'>🏥 نظام حجز المواعيد الذكي</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>تحدث مع المساعد الآلي لحجز موعدك مع أطباء مستشفى PSAU</p>", unsafe_allow_html=True)

# تقسيم الشاشة لتبويبات (المحادثة هي الأساس)
tab1, tab2 = st.tabs(["💬 حجز موعد جديد", "🔐 لوحة الإدارة"])

with tab1:
    # تهيئة سجل المحادثة
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "أنت مساعد مستشفى ذكي ومؤدب. ساعد المرضى في اختيار الطبيب المناسب وحجز الموعد. تحدث بالعربية الفصحى أو البيضاء."}
        ]

    # عرض الأطباء بشكل مختصر جداً في البداية كمرجع
    with st.expander("👨‍⚕️ استعراض الأطباء المتاحين"):
        conn = sqlite3.connect("hospital.db")
        docs = pd.read_sql_query("SELECT name, specialty, availability FROM doctors", conn)
        st.table(docs)
        conn.close()

    # عرض فقاعات المحادثة
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # مدخل الشات (Chat Input)
    if prompt := st.chat_input("أريد حجز موعد مع..."):
        # 1. إضافة رسالة المستخدم وعرضها
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. استجابة العميل الذكي (Agent Response)
        with st.chat_message("assistant"):
            response_placeholder = st.empty() # مكان لكتابة الرد أثناء المعالجة
            
            # طلب الرد من OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                tools=tools_schema
            )
            
            response_message = response.choices[0].message
            
            # معالجة استدعاء الدوال (إن وجدت)
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

                # الحصول على الرد النهائي بعد تنفيذ المهمة
                final_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages
                )
                reply = final_response.choices[0].message.content
            else:
                reply = response_message.content

            # عرض الرد النهائي وتخزينه
            response_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

with tab2:
    st.markdown("<h3 style='text-align: right;'>قسم الإدارة</h3>", unsafe_allow_html=True)
    admin_pwd = st.text_input("أدخل كلمة المرور للعرض", type="password")
    if admin_pwd == "saad2026":
        conn = sqlite3.connect("hospital.db")
        st.write("### قائمة المواعيد المسجلة")
        st.dataframe(pd.read_sql_query("SELECT * FROM appointments", conn), use_container_width=True)
        conn.close()
