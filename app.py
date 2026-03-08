import streamlit as st
from openai import OpenAI
import sqlite3
import pandas as pd
import json
from database import init_db
from tools import create_appointment, tools_schema

init_db()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Hospital Agentic AI", page_icon="🏥")
st.title("🏥 Hospital Agentic AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a hospital AI assistant. You help patients book appointments by calling the 'create_appointment' tool when they provide their info."}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

user_input = st.chat_input("كيف يمكنني مساعدتك في حجز موعد؟")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
        tools=tools_schema,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            function_args = json.loads(tool_call.function.arguments)
            
            # تنفيذ الحجز الفعلي في قاعدة البيانات
            result = create_appointment(
                name=function_args.get("name"),
                date=function_args.get("date"),
                time=function_args.get("time"),
                reason=function_args.get("reason")
            )
            
            st.session_state.messages.append(response_message)
            st.session_state.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": "create_appointment",
                "content": result
            })
            
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages
            )
            reply = second_response.choices[0].message.content
    else:
        reply = response_message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)

st.divider()
st.subheader("📊 لوحة مواعيد المستشفى (View Only)")
conn = sqlite3.connect("hospital.db")
df = pd.read_sql_query("SELECT * FROM appointments ORDER BY id DESC", conn)
st.dataframe(df, use_container_width=True)
conn.close()
