import streamlit as st
from openai import OpenAI
import os

from tools import create_appointment

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Clinic AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a clinic assistant that helps patients book appointments."}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask about appointments")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=st.session_state.messages
    )

    reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
