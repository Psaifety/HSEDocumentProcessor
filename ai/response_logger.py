"""JSONL logging for AI extraction requests and responses."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ResponseLogger:
    """Write safe AI response and error metadata to JSONL files."""

    def __init__(self, log_dir: Path | str) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.responses_file = self.log_dir / "responses.jsonl"
        self.errors_file = self.log_dir / "errors.jsonl"

    def log_success(
        self,
        *,
        model: str,
        prompt_name: str,
        response: Any,
        parsed_output: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a successful AI extraction without storing image payloads."""

        self._write(
            self.responses_file,
            {
                "event": "success",
                "timestamp": self._timestamp(),
                "model": model,
                "prompt_name": prompt_name,
                "response_id": getattr(response, "id", None),
                "usage": self._to_jsonable(getattr(response, "usage", None)),
                "parsed_output": self._to_jsonable(parsed_output),
                "metadata": metadata or {},
            },
        )

    def log_error(
        self,
        *,
        model: str,
        prompt_name: str,
        error: Exception,
        metadata: dict[str, Any] | None = None,
        response_id: str | None = None,
    ) -> None:
        """Log an AI extraction error without storing request payloads."""

        self._write(
            self.errors_file,
            {
                "event": "error",
                "timestamp": self._timestamp(),
                "model": model,
                "prompt_name": prompt_name,
                "response_id": response_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "metadata": metadata or {},
            },
        )

    def _write(self, path: Path, record: dict[str, Any]) -> None:
        """Append one JSON record to ``path``."""

        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=True, default=str))
            file.write("\n")

    @staticmethod
    def _timestamp() -> str:
        """Return the current UTC timestamp in ISO 8601 format."""

        return datetime.now(UTC).isoformat()

    @classmethod
    def _to_jsonable(cls, value: Any) -> Any:
        """Convert SDK and dataclass-like values to JSON-compatible data."""

        if value is None:
            return None

        if hasattr(value, "to_dict"):
            return cls._to_jsonable(value.to_dict())

        if hasattr(value, "model_dump"):
            return cls._to_jsonable(value.model_dump())

        if isinstance(value, dict):
            return {str(key): cls._to_jsonable(item) for key, item in value.items()}

        if isinstance(value, (list, tuple)):
            return [cls._to_jsonable(item) for item in value]

        if isinstance(value, Path):
            return str(value)

        return value
