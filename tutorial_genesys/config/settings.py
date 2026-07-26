from __future__ import annotations
"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True)

    # LLM — routed through the local `claude` CLI (Claude.ai subscription usage,
    # not Anthropic API credits). Requires `claude login` to have been run.
    writer_model: str = "claude-opus-4-6"
    classifier_model: str = "claude-haiku-4-5-20251001"

    # Tutorial Hunter integration
    hunter_api_url: str = "http://localhost:8000"
    hunter_db_path: str = "../ai-tutorial-hunter/tutorial_hunter.db"

    # ai-evolution.com.au deployment
    pulse_api_url: str = "https://ai-evolution.com.au/api"
    pulse_api_key: str = ""
    pulse_author_name: str = "The Pulse AI"
    pulse_category: str = "AI Guides"

    # Output
    output_dir: str = "./output"
    preview_port: int = 3000

    # Content
    max_tutorial_words: int = 5000
    min_tutorial_words: int = 2000
    log_level: str = "INFO"

    @property
    def output_path(self) -> Path:
        path = Path(self.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
