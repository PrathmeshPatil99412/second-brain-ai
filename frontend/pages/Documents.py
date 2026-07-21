"""Documents page — browse, view, summarize, delete."""
import streamlit as st

from utils.api_client import delete_document, get_document, list_documents, summarize_document

st.set_page_config(page_title="Documents", page_icon="📄", layout="wide")
st.title("📄 Documents")

try:
    docs_data = list_documents()
except Exception as e:
    st.error(f"Failed to load documents: {e}")
    st.stop()

if docs_data["total"] == 0:
    st.info("No documents uploaded yet. Go to the Upload page to add one.")
else:
    st.caption(f"{docs_data['total']} document(s)")

    for doc in docs_data["documents"]:
        with st.expander(f"📄 {doc['filename']} — {doc['status']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Size:** {doc['size_bytes']:,} bytes" if doc["size_bytes"] else "**Size:** unknown")
                st.write(f"**Type:** {doc['content_type']}")
            with col2:
                st.write(f"**Uploaded:** {doc['created_at']}")
                status_display = {"ready": "✅ Ready", "pending": "⏳ Pending", "processing": "🔄 Processing", "failed": "❌ Failed"}
                st.write(f"**Status:** {status_display.get(doc['status'], doc['status'])}")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("View details & summary", key=f"view_{doc['id']}"):
                    with st.spinner("Loading..."):
                        detail = get_document(doc["id"])
                        if detail.get("summary"):
                            st.markdown(f"**Summary:** {detail['summary']}")
                        else:
                            st.info("No summary yet.")
                        if detail.get("tags"):
                            st.write("**Tags:** " + ", ".join(detail["tags"]))

            with col_b:
                if st.button("Generate summary & tags", key=f"summarize_{doc['id']}"):
                    with st.spinner("Generating summary..."):
                        try:
                            result = summarize_document(doc["id"])
                            st.success(result["message"])
                            st.markdown(f"**Summary:** {result['summary']}")
                        except Exception as e:
                            st.error(f"Summarization failed: {e}")

            if st.button("🗑️ Delete", key=f"delete_{doc['id']}", type="secondary"):
                try:
                    delete_document(doc["id"])
                    st.success("Deleted. Refresh the page to update the list.")
                except Exception as e:
                    st.error(f"Delete failed: {e}")
