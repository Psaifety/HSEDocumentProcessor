"""Processing result model for document pipeline runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from models.document_type import DocumentType
from models.training_record import TrainingRecord


@dataclass(frozen=True)
class ProcessingResult:
    """Structured result returned by the document processing pipeline."""

    pdf_path: Path
    document_type: DocumentType
    training_record: TrainingRecord | None
    success: bool
    error_message: str | None
    processing_time_seconds: float
    image_path: Path | None = None
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the result."""

        data = asdict(self)
        data["pdf_path"] = str(self.pdf_path)
        data["document_type"] = self.document_type.value
        data["training_record"] = (
            self.training_record.to_dict() if self.training_record else None
        )
        data["image_path"] = str(self.image_path) if self.image_path else None
        return data
