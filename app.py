"""
Day 8: the chat UI in the browser.

Run:  streamlit run app.py      (opens http://localhost:8501)

Frontend only: the page is drawn by src/ui/, all the work is done by the same
ChatSession that chat.py uses in the terminal.
"""

import streamlit as st

from src import config
from src.ui import current_session, render_chat, render_sidebar

st.set_page_config(page_title="RAG Chatbot", page_icon="📄", layout="wide")
st.title("📄 RAG Chatbot: papers → slides, scripts & notes")
st.caption(f"Every fact is cited [chunk ID] and checked against the paper · edits show old vs new and why · "
           f"model: {config.LLM_MODEL} · conversations are saved to logs/")

chat = current_session()
render_sidebar(chat)
render_chat(chat)
