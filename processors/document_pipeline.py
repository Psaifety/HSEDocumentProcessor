"""Document processing pipeline orchestration."""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter

from ai import AIExtractionEngine
from models import DocumentType, ProcessingResult, TrainingRecord
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
        document_type = DocumentType.UNKNOWN
        image_path: Path | None = None

        logger.info("Starting document processing: %s", path)

        try:
            if not path.exists() or not path.is_file():
                raise FileNotFoundError(f"PDF file does not exist: {path}")

            document_type = DocumentType.from_value(self.classifier.classify(path))
            rendered_page = self.pdf_processor.render_first_page(path)
            image_path = rendered_page.image_path

            extraction_data = self.ai_engine.extract(
                document_type=document_type.value,
                image=rendered_page.image,
                metadata={
                    "pdf_path": str(path),
                    "document_type": document_type.value,
                },
            )
            training_record = TrainingRecord.from_dict(
                extraction_data,
                document_type=document_type,
            )

            result = ProcessingResult(
                pdf_path=path,
                document_type=document_type,
                training_record=training_record,
                success=True,
                error_message=None,
                processing_time_seconds=perf_counter() - start_time,
                image_path=image_path,
                confidence=training_record.confidence,
            )
        except Exception as exc:
            result = ProcessingResult(
                pdf_path=path,
                document_type=document_type,
                training_record=None,
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
