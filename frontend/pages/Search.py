"""Search page — semantic search over documents and notes."""
import streamlit as st

from utils.api_client import semantic_search

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
st.title("🔍 Semantic Search")

query = st.text_input("Search your knowledge base")
top_k = st.slider("Number of results", min_value=1, max_value=20, value=5)

if st.button("Search", type="primary") and query:
    with st.spinner("Searching..."):
        try:
            result = semantic_search(query, top_k)
            st.caption(f"{result['total']} results for \"{result['query']}\"")

            for item in result["results"]:
                label = item["metadata"].get("filename") or item["metadata"].get("title") or "Unknown source"
                with st.container(border=True):
                    st.markdown(f"**{label}** — relevance: {item['score']}")
                    st.write(item["content"])
        except Exception as e:
            st.error(f"Search failed: {e}")
