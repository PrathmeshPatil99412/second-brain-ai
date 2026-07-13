"""Centralized application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory.
# __file__ -> current file (config.py)
# .parent -> app/core/
# .parent.parent -> app/
# .parent.parent.parent -> project root/
#
# Using BASE_DIR avoids hardcoding absolute or relative paths throughout
# the project.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application-wide settings loaded from the .env file."""

    # Read environment variables from the project's .env file.
    # Ignore any extra variables that are not defined in this class.
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        extra="ignore",
    )

    # ===== AI Model =====
    gemini_api_key: str
    gemini_chat_model: str = "gemini-2.5-flash"

    # ===== Project Data Directories =====
    # Keeping all paths relative to BASE_DIR makes the project portable.
    data_dir: Path = BASE_DIR / "data"
    uploads_dir: Path = data_dir / "uploads"
    chroma_dir: Path = data_dir / "chroma"
    sqlite_path: Path = data_dir / "sqlite" / "second_brain.db"

    # ===== RAG Configuration =====
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k_default: int = 5


# Cache the Settings instance so the .env file is parsed only once.
# Every call to get_settings() returns the same Settings object,
# avoiding repeated initialization.
@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()