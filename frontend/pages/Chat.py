import streamlit as st


from utils.api_client import chat_query

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")
st.title("💬 Chat with your knowledge base")

if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": ..., "content": ..., "sources": [...]}

# Render existing conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"Sources ({len(msg['sources'])})"):
                for src in msg["sources"]:
                    label = src["metadata"].get("filename") or src["metadata"].get("title") or "Unknown source"
                    st.markdown(f"**{label}** — score: {src['score']}")
                    st.caption(src["content"][:300] + "...")

# Chat input
if query := st.chat_input("Ask a question about your documents and notes..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Build history in the shape the API expects (exclude sources, just role/content)
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]  # exclude the just-added user message
                ]
                result = chat_query(query, history)
                st.markdown(result["answer"])
                if result["sources"]:
                    with st.expander(f"Sources ({len(result['sources'])})"):
                        for src in result["sources"]:
                            label = src["metadata"].get("filename") or src["metadata"].get("title") or "Unknown source"
                            st.markdown(f"**{label}** — score: {src['score']}")
                            st.caption(src["content"][:300] + "...")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                })
            except Exception as e:
                st.error(f"Chat failed: {e}")