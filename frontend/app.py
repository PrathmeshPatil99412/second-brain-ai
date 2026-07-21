"""Second Brain AI — main entry point."""
import streamlit as st

st.set_page_config(
    page_title="Second Brain AI",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Second Brain AI")
st.markdown(
    """
    Welcome to your AI-powered personal knowledge management system.

    **Use the sidebar to navigate:**
    - 📤 **Upload** — add documents and notes to your knowledge base
    - 💬 **Chat** — ask questions and get grounded answers with citations
    - 🔍 **Search** — semantic search across everything you've saved
    - 📄 **Documents** — browse, view, and manage your uploaded files
    - 📊 **Dashboard** — see stats about your knowledge base
    """
)