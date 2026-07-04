"""Prompt loading utilities for AI extraction."""

from __future__ import annotations

from pathlib import Path


class PromptNotFoundError(FileNotFoundError):
    """Raised when a requested prompt file does not exist."""


class PromptLoader:
    """Load Markdown prompts from the configured prompt directory."""

    def __init__(self, prompts_dir: Path | str) -> None:
        self.prompts_dir = Path(prompts_dir).resolve()

    def load(self, prompt_name: str) -> str:
        """Return the Markdown prompt text for ``prompt_name``."""

        prompt_path = self.resolve(prompt_name)

        if not prompt_path.exists():
            raise PromptNotFoundError(f"Prompt not found: {prompt_path}")

        return prompt_path.read_text(encoding="utf-8").strip()

    def resolve(self, prompt_name: str) -> Path:
        """Resolve a prompt name to a safe Markdown file path."""

        prompt_path = Path(prompt_name)

        if prompt_path.suffix != ".md":
            prompt_path = prompt_path.with_suffix(".md")

        resolved_path = (self.prompts_dir / prompt_path).resolve()

        try:
            resolved_path.relative_to(self.prompts_dir)
        except ValueError as exc:
            raise ValueError("Prompt paths must stay inside the prompts directory.") from exc

        return resolved_path
