"""Application settings loaded from environment files."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_MODEL = "gpt-5.5"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = PROJECT_ROOT / "config" / ".env"


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for AI-backed extraction."""

    openai_api_key: str | None
    openai_model: str
    project_root: Path
    prompts_dir: Path
    ai_log_dir: Path


def load_settings(
    env_file: Path | str | None = None,
    *,
    override: bool = False,
    project_root: Path | str | None = None,
) -> Settings:
    """Load settings from ``config/.env`` and the current process environment.

    The function intentionally does not raise when ``OPENAI_API_KEY`` is
    missing. That lets non-AI workflows and unit tests import the project
    without requiring credentials.
    """

    root = Path(project_root).resolve() if project_root else PROJECT_ROOT
    env_path = Path(env_file).resolve() if env_file else root / "config" / ".env"

    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=override)

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        project_root=root,
        prompts_dir=root / "prompts",
        ai_log_dir=root / "logs" / "ai",
    )
