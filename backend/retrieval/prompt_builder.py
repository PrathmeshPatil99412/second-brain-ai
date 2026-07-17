"""
Builds the actual prompt text sent to Gemini for chat queries.
"""

_SYSTEM_INSTRUCTION = (
    "You are a helpful assistant answering questions using ONLY the provided "
    "context from the user's personal documents. If the context doesn't contain "
    "enough information to answer, say so clearly instead of guessing. "
    "Be concise and cite which source you're drawing from when relevant."
)


def build_chat_prompt(query: str, retrieved_chunks: list[dict], chat_history: list[dict] | None = None) -> str:
    """
    Construct the full prompt: retrieved context + chat history + the question.

    retrieved_chunks: output of retriever.retrieve_top_k()
    chat_history: list of {"role": "user"/"assistant", "content": str}
    """
    context_block = _format_context(retrieved_chunks)
    history_block = _format_history(chat_history) if chat_history else ""

    prompt = (
        f"Context from your documents:\n{context_block}\n\n"
        f"{history_block}"
        f"Question: {query}\n\n"
        f"Answer based on the context above:"
    )
    return prompt


def get_system_instruction() -> str:
    return _SYSTEM_INSTRUCTION


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "(No relevant context found in your documents.)"

    parts = []
    for i, chunk in enumerate(chunks, start=1):
        filename = chunk["metadata"].get("filename", "unknown source")
        parts.append(f"[Source {i} — {filename}]\n{chunk['content']}")
    return "\n\n".join(parts)


def _format_history(history: list[dict]) -> str:
    if not history:
        return ""
    lines = [f"{turn['role'].capitalize()}: {turn['content']}" for turn in history]
    return "Previous conversation:\n" + "\n".join(lines) + "\n\n"