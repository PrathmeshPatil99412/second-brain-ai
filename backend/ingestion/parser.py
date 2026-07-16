"""
PDF text extraction using PyMuPDF (fitz).
"""
import fitz  # PyMuPDF

from utils.logger import get_logger

logger = get_logger(__name__)


def extract_text(file_path: str) -> str:
    """
    Extract all text from a PDF, page by page, with light cleaning.
    Returns one combined string for the whole document.
    """
    doc = fitz.open(file_path)
    pages_text = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages_text.append(text)

    doc.close()

    full_text = "\n\n".join(pages_text)
    cleaned = _clean_text(full_text)

    logger.info(f"Extracted {len(cleaned)} chars from {len(pages_text)} pages ({file_path})")
    return cleaned


def _clean_text(text: str) -> str:
    """Strip null bytes and collapse excessive whitespace."""
    text = text.replace("\x00", "")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]  # drop empty lines
    return "\n".join(lines)


if __name__ == "__main__":
    # Standalone test — run from backend/:
    #   python -m ingestion.parser
    # REQUIRES: put one real PDF at data/uploads/test.pdf first
    test_path = "../data/uploads/test.pdf"
    text = extract_text(test_path)
    print(f"Total chars extracted: {len(text)}")
    print("\nFirst 500 chars:\n")
    print(text[:500])