"""
chat_view.py - the main panel: the conversation so far + the message box.

The conversation is drawn from ChatSession's log (the same turns saved to logs/),
so the page keeps no copy of its own. Replies are Markdown: diffs (~~old~~ **new**)
and LaTeX ($$...$$) render as they are. st.markdown does not run HTML, so text
from the LLM cannot inject anything into the page.
"""

import streamlit as st

from src.conversation import ChatSession
from src.conversation.session import HELP


def render_chat(chat: ChatSession) -> None:
    if not chat.log.turns:
        with st.chat_message("assistant"):
            st.markdown("👋 " + HELP)
    for turn in chat.log.turns:
        st.chat_message("user").markdown(turn.user)
        st.chat_message("assistant").markdown(turn.reply)

    message = st.chat_input("e.g. make #2 less technical") or st.session_state.pop("pending", None)
    if message:
        st.chat_message("user").markdown(message)
        with st.chat_message("assistant"), st.spinner("Working on it - retrieving, writing, checking (10-60 s)..."):
            chat.handle(message)  # the reply is added to chat.log
        st.rerun()  # redraw everything (the new turn, the sidebar downloads)
