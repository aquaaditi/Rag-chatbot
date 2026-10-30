"""
sidebar.py - the left panel: upload a paper, see the papers, example requests,
downloads (current talk + conversation log) and "new conversation".
"""

import hashlib

import streamlit as st

from src import config
from src.conversation import ChatSession
from src.talks.export import talk_to_markdown
from src.ui.state import new_conversation, shared_retriever, uploaded_papers
from src.upload import add_paper

EXAMPLES = [
    "Make a 5-slide talk on the fastText paper for policymakers",
    "Make a 7-slide talk on the distillation paper for graduate students focusing on methods; "
    "include 3 speaker notes per slide and preserve key equations",
    "make #2 less technical",
    "shorten the script to 90 seconds",
    "history",
    "undo",
]


def render_sidebar(chat: ChatSession) -> None:
    with st.sidebar:
        _upload_box()
        st.subheader("📚 Papers")
        for paper_id, title in chat.papers.items():
            st.markdown(f"**{paper_id}** · {title}...")
        _examples()
        _downloads(chat)
        st.divider()
        if st.button("🗑️ New conversation", width="stretch"):
            new_conversation()
            st.rerun()


def _upload_box() -> None:
    file = st.file_uploader(f"Add a paper (.pdf or .tex, max {config.MAX_UPLOAD_MB} MB)", type=["pdf", "tex"])
    if file is None:
        return
    data = file.getvalue()
    key = hashlib.sha256(data).hexdigest()  # same content = same paper, whatever the file name
    added = uploaded_papers()
    if key not in added:
        with st.spinner(f"Reading and indexing {file.name}..."):
            try:
                added[key] = add_paper(file.name, data, shared_retriever())
            except ValueError as error:
                st.error(str(error))
                return
    result = added[key]
    st.success(f"{file.name} is **{result.paper_id}**: {result.n_chunks} chunks "
               f"({result.n_math} with equations). Ask e.g. \"Make a 5-slide talk on {result.paper_id}\".")
    if result.dropped:
        st.warning(f"🛡️ Removed {len(result.dropped)} chunk(s) that contained instructions to the AI: "
                   + ", ".join(result.dropped))


def _examples() -> None:
    st.subheader("💡 Try")
    for example in EXAMPLES:
        if st.button(example, width="stretch"):
            st.session_state.pending = example  # picked up by the chat view below


def _downloads(chat: ChatSession) -> None:
    st.subheader("⬇️ Download")
    result = chat.current_result()
    st.download_button(
        "Current talk (.md)", talk_to_markdown(result) if result else "", width="stretch",
        file_name=f"talk_v{chat.history.current.number}.md" if result else "talk.md",
        mime="text/markdown", disabled=result is None,
    )
    st.download_button(
        "Conversation log (.md)", chat.log.to_markdown(), width="stretch",
        file_name=chat.log.md_path.name, mime="text/markdown", disabled=not chat.log.turns,
    )
