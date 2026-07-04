"""
Batch processing result model.

Represents the outcome of processing an entire folder of training
documents through the DocumentPipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from models.processing_result import ProcessingResult


@dataclass
class BatchResult:
    """
    Represents the result of processing an entire batch of PDFs.
    """

    results: List[ProcessingResult] = field(default_factory=list)
    processing_time_seconds: float = 0.0

    @property
    def total_documents(self) -> int:
        """Total number of documents processed."""
        return len(self.results)

    @property
    def successful_results(self) -> List[ProcessingResult]:
        """Returns all successful processing results."""
        return [r for r in self.results if r.success]

    @property
    def failed_results(self) -> List[ProcessingResult]:
        """Returns all failed processing results."""
        return [r for r in self.results if not r.success]

    @property
    def successful_documents(self) -> int:
        """Number of successful documents."""
        return len(self.successful_results)

    @property
    def failed_documents(self) -> int:
        """Number of failed documents."""
        return len(self.failed_results)

    @property
    def success_rate(self) -> float:
        """Percentage of successful documents."""
        if self.total_documents == 0:
            return 0.0

        return round(
            (self.successful_documents / self.total_documents) * 100,
            2
        )
    
    @property
    def average_processing_time(self) -> float:

        if self.total_documents == 0:
            return 0.0

        return round(
            self.processing_time_seconds /
            self.total_documents,
             2,
        )

    def to_dict(self) -> dict:
        """Serialise the batch result."""


        
        return {
            "total_documents": self.total_documents,
            "successful_documents": self.successful_documents,
            "failed_documents": self.failed_documents,
            "success_rate": self.success_rate,
            "processing_time_seconds": round(
                self.processing_time_seconds,
                2,
            ),
            "average_processing_time": self.average_processing_time,
            "results": [
                r.to_dict()
                for r in self.results
            ],
        }

    def __str__(self) -> str:

        return (
            f"BatchResult("
            f"{self.successful_documents}/{self.total_documents} successful, "
            f"{self.failed_documents} failed, "
            f"{self.processing_time_seconds:.2f}s)"
        )