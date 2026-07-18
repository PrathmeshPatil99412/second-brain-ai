"""Auto-tag generation using Gemini."""
from intelligence.gemini import generate_text

_TAG_INSTRUCTION = (
    "You generate short topical tags for documents. "
    "Return ONLY a comma-separated list of 3-5 lowercase tags, no other text."
)


def generate_tags(text: str) -> list[str]:
    truncated = text[:8000]
    prompt = f"Generate tags for this text:\n\n{truncated}"
    raw = generate_text(prompt, system_instruction=_TAG_INSTRUCTION, temperature=0.2)

    if raw.startswith("["):  # fallback message from gemini.py error handling (e.g. overload/error)
        return []

    tags = [t.strip().lower() for t in raw.split(",") if t.strip()]
    return tags