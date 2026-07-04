"""Processing result model for document pipeline runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProcessingResult:
    """Structured result returned by the document processing pipeline."""

    pdf_path: Path
    document_type: str
    extracted_data: dict[str, Any]
    success: bool
    error_message: str | None
    processing_time_seconds: float
    image_path: Path | None = None
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the result."""

        data = asdict(self)
        data["pdf_path"] = str(self.pdf_path)
        data["image_path"] = str(self.image_path) if self.image_path else None
        return data
