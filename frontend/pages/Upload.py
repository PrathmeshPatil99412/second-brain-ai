"""Upload page — documents and notes."""
import streamlit as st

from utils.api_client import upload_document, create_note

st.set_page_config(page_title="Upload", page_icon="📤", layout="wide")
st.title("📤 Upload")

tab_doc, tab_note = st.tabs(["📄 Upload Document", "📝 Create Note"])

with tab_doc:
    st.subheader("Upload a PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Upload and process", type="primary"):
            with st.spinner("Parsing, chunking, and embedding your document..."):
                try:
                    result = upload_document(uploaded_file)
                    if result["status"] == "ready":
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

with tab_note:
    st.subheader("Create a note")
    title = st.text_input("Title")
    content = st.text_area("Content", height=200)
    folder = st.text_input("Folder (optional)")

    if st.button("Save note", type="primary"):
        if not title or not content:
            st.warning("Title and content are required.")
        else:
            with st.spinner("Saving and indexing your note..."):
                try:
                    result = create_note(title, content, folder or None)
                    if result["status"] == "ready":
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['message']}")
                except Exception as e:
                    st.error(f"Failed to save note: {e}")