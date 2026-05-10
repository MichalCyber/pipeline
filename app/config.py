import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
from typing import List

load_dotenv()


def _parse_bool(value: str, default=False) -> bool:
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def _parse_list(value: str) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


@dataclass(slots=True)
class Settings:
    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
    API_KEYS: List[str] = field(
        default_factory=lambda: os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
    )

    # ------------------------------------------------------------------
    # Collectors
    # ------------------------------------------------------------------
    USE_YTDLP: bool = os.getenv("USE_YTDLP", "true").lower() == "true"
    YOUTUBE_API_KEY: str | None = os.getenv("YOUTUBE_API_KEY")

    USER_AGENTS: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)"
    ])

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./outputs")
    JOBS_DIR: str = os.getenv("JOBS_DIR", "./outputs/jobs")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./outputs/pipeline.db")

    # ------------------------------------------------------------------
    # Fooocus
    # ------------------------------------------------------------------
    FOOOCUS_URL: str = os.getenv("FOOOCUS_URL", "http://127.0.0.1:7865")


# Singleton
settings = Settings()