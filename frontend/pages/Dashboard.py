"""Dashboard page — knowledge base stats."""
import streamlit as st

from utils.api_client import get_dashboard_stats

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard")

try:
    stats = get_dashboard_stats()
except Exception as e:
    st.error(f"Failed to load dashboard: {e}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Documents", stats["total_documents"])
col2.metric("Notes", stats["total_notes"])
col3.metric("Chunks", stats["total_chunks"])
col4.metric("Storage used", f"{stats['storage_used_bytes'] / 1024:.1f} KB")

st.subheader("Documents by status")
if stats["documents_by_status"]:
    for status, count in stats["documents_by_status"].items():
        st.write(f"**{status.capitalize()}:** {count}")
else:
    st.info("No documents yet.")