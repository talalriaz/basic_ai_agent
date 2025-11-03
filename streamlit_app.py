import streamlit as st
import requests
import json
from datetime import datetime

# --- Configuration ---
API_URL = "http://localhost:8000/chat"  # Change if your FastAPI runs elsewhere
CLEAR_SESSION_URL = "http://localhost:8000/session/{session_id}"

st.set_page_config(page_title="AI Agent Chat", page_icon="🤖", layout="centered")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# --- Sidebar: Session Management ---
with st.sidebar:
    st.header("Session Control")
    
    name = st.text_input("Your Name (optional)", value=st.session_state.user_name)
    if name != st.session_state.user_name:
        st.session_state.user_name = name
        st.rerun()

    if st.button("New Chat", type="primary"):
        if st.session_state.session_id:
            try:
                requests.delete(CLEAR_SESSION_URL.format(session_id=st.session_state.session_id))
            except:
                pass
        st.session_state.messages = []
        st.session_state.session_id = None
        st.success("New chat started!")
        st.rerun()

    if st.session_state.session_id:
        st.info(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
        if st.button("Copy Session ID"):
            st.code(st.session_state.session_id, language=None)
    else:
        st.info("No active session")

    st.markdown("---")
    st.caption(f"Connected to: `{API_URL.split('/chat')[0]}`")

# --- Main Chat Interface ---
st.title("🤖 AI Agent Chat")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "timestamp" in message:
            st.caption(message["timestamp"])

# Chat input
if prompt := st.chat_input("Ask something..."):
    # Add user message
    user_msg = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(user_msg["timestamp"])

    # Prepare request
    payload = {
        "message": prompt,
        "session_id": st.session_state.session_id
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    session_id = data["session_id"]

                    # Update session ID if new
                    if st.session_state.session_id is None:
                        st.session_state.session_id = session_id

                    # Display assistant response
                    st.markdown(answer)
                    st.caption(datetime.now().strftime("%H:%M:%S"))

                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

                else:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {error_msg}",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

            except requests.exceptions.RequestException as e:
                error_msg = f"Connection error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {error_msg}",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })