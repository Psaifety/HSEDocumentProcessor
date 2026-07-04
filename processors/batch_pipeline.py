"""
Batch processing pipeline.

Processes an entire folder of PDFs using the existing
DocumentPipeline.
"""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter
from typing import Callable

from models.batch_result import BatchResult
from processors.document_pipeline import DocumentPipeline

logger = logging.getLogger(__name__)


class BatchPipeline:
    """
    Processes every PDF in a folder.
    """

    def __init__(
        self,
        *,
        document_pipeline: DocumentPipeline | None = None,
    ) -> None:

        self.document_pipeline = document_pipeline or DocumentPipeline()

    def process_folder(
        self,
        folder: Path,
        progress_callback: Callable[[int, int, Path], None] | None = None,
    ) -> BatchResult:

        start_time = perf_counter()

        folder = Path(folder)

        if not folder.exists():
            raise FileNotFoundError(folder)

        if not folder.is_dir():
            raise NotADirectoryError(folder)

        pdf_files = sorted(folder.rglob("*.pdf"))

        logger.info(
            "Starting batch processing (%s PDFs)",
            len(pdf_files),
        )

        results = []

        total = len(pdf_files)

        for index, pdf in enumerate(pdf_files, start=1):

            logger.info(
                "[%s/%s] %s",
                index,
                total,
                pdf.name,
            )

            result = self.document_pipeline.process(pdf)

            results.append(result)

            if progress_callback:

                progress_callback(
                    index,
                    total,
                    pdf,
                )

        elapsed = perf_counter() - start_time

        logger.info(
            "Batch completed in %.2fs",
            elapsed,
        )

        return BatchResult(
            results=results,
            processing_time_seconds=elapsed,
        )