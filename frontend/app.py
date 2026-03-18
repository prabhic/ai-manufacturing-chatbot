"""
Streamlit Frontend — Mentor AI Chatbot UI

A clean chat interface that talks to the FastAPI backend.
Run with: streamlit run frontend/app.py
"""

import os

import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# In Cloud Run, set BACKEND_URL env var to the backend service URL.
# Falls back to localhost for local development.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Manufacturing AI Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Manufacturing AI Chatbot")
st.caption("Powered by Gemini with Tool Calling")

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

# experimental_rerun
def refresh_page():
    print("🔄 Refreshing page...")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()

    st.button("🔄 Refresh", use_container_width=True, on_click=refresh_page)

    st.divider()
    st.markdown("**Available Tools:**")
    st.markdown("- ⏰ `get_current_time`")
    st.markdown("this front demostrates streamlit python framework")
    st.divider()
    st.markdown(
        "Built with **FastAPI** + **Streamlit**  \n"
        "AI by **Google Gemini**"
    )



# ---------------------------------------------------------------------------
# Display chat history
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tool_used"):
            with st.expander(f"🔧 Tool used: `{msg['tool_used']}`"):
                st.info(f"The AI called the **{msg['tool_used']}** tool to answer this question.")

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
if user_input := st.chat_input("Type your message..."):
    # Display user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call backend API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={
                        "message": user_input,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                print(data)

                # Update session ID
                st.session_state.session_id = data["session_id"]

                # Display response
                assistant_text = data["response"]

                st.markdown("Below message received from Gemini API")
                st.markdown(assistant_text)

                # Show tool usage if applicable
                tool_used = data.get("tool_used")
                if tool_used:
                    with st.expander(f"🔧 Tool used: `{tool_used}`"):
                        st.info(f"The AI called the **{tool_used}** tool to answer this question.")

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_used": tool_used,
                })

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to the backend. "
                    "Make sure the FastAPI server is running:\n\n"
                    "```\nuvicorn backend.main:app --reload --port 8000\n```"
                )
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Backend error: {e.response.text}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")
