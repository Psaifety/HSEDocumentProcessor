"""Document processing pipeline orchestration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from processors.document_processor import DocumentProcessor
from processors.document_reader import DocumentReader
from processors.document_writer import DocumentWriter

if TYPE_CHECKING:
    from models.training_record import TrainingRecord


class DocumentPipeline:
    def __init__(
        self,
        reader: DocumentReader,
        processor: DocumentProcessor,
        writer: DocumentWriter,
    ):
        self.reader = reader
        self.processor = processor
        self.writer = writer
        self.logger = logging.getLogger(__name__)

    def run(self, input_path: str, output_path: str) -> None:
        self.logger.info("Starting document pipeline")
        documents = self.reader.read_documents(input_path)
        self.logger.info(f"Read {len(documents)} documents")

        processed_records: list[TrainingRecord] = []
        for document in documents:
            try:
                record = self.processor.process(document)
                processed_records.append(record)
            except Exception as e:
                self.logger.error(f"Failed to process document {document.id}: {e}")

        self.writer.write_records(processed_records, output_path)
        self.logger.info("Document pipeline completed")
