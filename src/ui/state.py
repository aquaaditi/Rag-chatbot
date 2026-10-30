"""
state.py - what the web page remembers between clicks.

Streamlit re-runs app.py from the top on EVERY click or message, so anything
that must survive is kept in one of two places:

    st.cache_resource   shared by the whole app, created once (the retriever: loading
                        the embedding model takes ~10 s, so it must not reload per click)
    st.session_state    one per browser tab (the ChatSession = this user's conversation)
"""

import streamlit as st

from src.conversation import ChatSession
from src.retrieval import Retriever
from src.upload import UploadResult


@st.cache_resource(show_spinner="Loading the papers and the embedding model...")
def shared_retriever() -> Retriever:
    """One retriever for the app. Uploaded papers are added to it, so every tab sees them
    (fine for a local demo; a multi-user server would keep one index per user)."""
    return Retriever.load()


@st.cache_resource
def uploaded_papers() -> dict[str, UploadResult]:
    """{file hash: result} - the same file is never added twice, even after a re-run."""
    return {}


def current_session() -> ChatSession:
    if "chat" not in st.session_state:
        new_conversation()
    return st.session_state.chat


def new_conversation() -> None:
    st.session_state.chat = ChatSession(shared_retriever())
