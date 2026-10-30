"""
UI (frontend):  the Streamlit chat page. It only SHOWS things - every decision
is made by the backend (ChatSession in src/conversation/).

    state.py      what survives Streamlit's re-runs (shared retriever, one ChatSession per tab)
    sidebar.py    upload a paper, paper list, examples, downloads, new conversation
    chat_view.py  the conversation + message box

app.py only needs these three functions.
"""

from src.ui.chat_view import render_chat
from src.ui.sidebar import render_sidebar
from src.ui.state import current_session

__all__ = ["current_session", "render_chat", "render_sidebar"]
