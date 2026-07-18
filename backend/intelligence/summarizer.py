"""Document/note summarization using Gemini."""
from intelligence.gemini import generate_text

_SUMMARY_INSTRUCTION = (
    "You summarize documents concisely and accurately. "
    "Produce a 3-5 sentence summary capturing the key points. No preamble."
)


def summarize_text(text: str) -> str:
    # Guard against extremely long documents blowing the prompt — truncate if needed
    truncated = text[:15000]
    prompt = f"Summarize the following text:\n\n{truncated}"
    return generate_text(prompt, system_instruction=_SUMMARY_INSTRUCTION, temperature=0.3)