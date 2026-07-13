"""
Gemini client wrapper — handles text GENERATION only.
"""
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_client = genai.Client(api_key=settings.gemini_api_key)


def generate_text(
    prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.3,
) -> str:
    """
    Send a prompt to Gemini, return the generated text.

    Returns a clear fallback message instead of raising, if Gemini is
    unreachable or overloaded — so callers (chat route, summary route)
    can still respond to the user instead of crashing with a 500.
    """
    logger.info(f"Sending prompt to Gemini (model={settings.gemini_chat_model}, len={len(prompt)} chars)")

    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
    )

    try:
        response = _client.models.generate_content(
            model=settings.gemini_chat_model,
            contents=prompt,
            config=config,
        )
        text = response.text or ""
        logger.info(f"Received response from Gemini (len={len(text)} chars)")
        return text

    except ServerError as e:
        # 500/503 from Google's side — model overloaded, temporary outage, etc.
        # NOT our bug, and retrying immediately usually won't help either.
        logger.error(f"Gemini server error (likely overloaded): {e}")
        return "[Gemini is currently overloaded or unavailable. Please try again in a moment.]"

    except ClientError as e:
        # 4xx errors — bad API key, invalid model name, malformed request, quota exceeded.
        # THIS is usually our bug (or a config issue) and worth looking at immediately.
        logger.error(f"Gemini client error (check API key/model/request): {e}")
        return "[Gemini request failed — check API key, model name, or request format.]"

    except Exception as e:
        # Catch-all for anything unexpected (network timeout, etc.)
        logger.error(f"Unexpected error calling Gemini: {e}")
        return "[Unexpected error contacting Gemini.]"


if __name__ == "__main__":
    print("Testing Gemini connection...")
    test_answer = generate_text(
        prompt="In one short sentence, what is a second brain in the context of personal knowledge management?",
    )
    print("\nGemini response:")
    print(test_answer)