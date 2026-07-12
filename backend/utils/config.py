"""Centralized application configuration loaded from environment variables."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root (second-brain-ai/)


class Settings(BaseSettings):
    """App-wide settings, loaded once from .env and cached."""

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    gemini_api_key: str
    gemini_chat_model: str = "gemini-2.5-flash"

    data_dir: Path = BASE_DIR / "data"
    uploads_dir: Path = BASE_DIR / "data" / "uploads"
    chroma_dir: Path = BASE_DIR / "data" / "chroma"
    sqlite_path: Path = BASE_DIR / "data" / "sqlite" / "second_brain.db"

    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k_default: int = 5


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (parsed once per process)."""
    return Settings()