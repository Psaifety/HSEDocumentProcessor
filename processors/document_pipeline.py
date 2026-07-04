"""Document processing pipeline orchestration."""

from __future__ import annotations

import logging
from dataclasses import asdict, is_dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from ai import AIExtractionEngine
from models import ProcessingResult
from processors.document_classifier import DocumentClassifier
from processors.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)


class DocumentPipeline:
    """Run classification, rendering, and AI extraction for a single PDF."""

    def __init__(
        self,
        *,
        classifier: DocumentClassifier | None = None,
        pdf_processor: PDFProcessor | None = None,
        ai_engine: AIExtractionEngine | None = None,
    ) -> None:
        self.classifier = classifier or DocumentClassifier()
        self.pdf_processor = pdf_processor or PDFProcessor()
        self.ai_engine = ai_engine or AIExtractionEngine()

    def process(self, pdf_path: Path) -> ProcessingResult:
        """Process one PDF from classification through AI extraction."""

        start_time = perf_counter()
        path = Path(pdf_path)
        document_type = "Unknown"
        image_path: Path | None = None

        logger.info("Starting document processing: %s", path)

        try:
            if not path.exists() or not path.is_file():
                raise FileNotFoundError(f"PDF file does not exist: {path}")

            document_type = self.classifier.classify(path)
            rendered_page = self.pdf_processor.render_first_page(path)
            image_path = rendered_page.image_path

            extraction = self.ai_engine.extract(
                document_type=document_type,
                image=rendered_page.image,
                metadata={
                    "pdf_path": str(path),
                    "document_type": document_type,
                },
            )
            extracted_data = _to_dict(extraction)
            confidence = _extract_confidence(extracted_data)

            result = ProcessingResult(
                pdf_path=path,
                document_type=document_type,
                extracted_data=extracted_data,
                success=True,
                error_message=None,
                processing_time_seconds=perf_counter() - start_time,
                image_path=image_path,
                confidence=confidence,
            )
        except Exception as exc:
            result = ProcessingResult(
                pdf_path=path,
                document_type=document_type,
                extracted_data={},
                success=False,
                error_message=str(exc),
                processing_time_seconds=perf_counter() - start_time,
                image_path=image_path,
                confidence=None,
            )

        logger.info(
            "Finished document processing: %s success=%s elapsed=%.2fs",
            path,
            result.success,
            result.processing_time_seconds,
        )

        return result


def _to_dict(value: Any) -> dict[str, Any]:
    """Convert an extraction object into a dictionary."""

    if isinstance(value, dict):
        return value

    if hasattr(value, "to_dict"):
        return value.to_dict()

    if is_dataclass(value):
        return asdict(value)

    raise TypeError(f"Unsupported extraction result type: {type(value).__name__}")


def _extract_confidence(extracted_data: dict[str, Any]) -> float | None:
    """Return a generic confidence value from extraction data when present."""

    confidence = extracted_data.get("confidence")

    if isinstance(confidence, int | float):
        return float(confidence)

    return None
