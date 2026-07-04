"""Tests for the TrainingRecord business model."""

from __future__ import annotations

import json
import unittest
from datetime import date

from models import DocumentType, TrainingRecord


class TrainingRecordTests(unittest.TestCase):
    """Unit tests for TrainingRecord creation and serialization."""

    def test_creation(self) -> None:
        record = TrainingRecord(
            document_type=DocumentType.TASK_SPECIFIC_HSE_TRAINING,
            training_subject="Working at Height",
            trainer="A. Trainer",
            date=date(2025, 4, 28),
            duration_text="1 hour",
            confidence=0.91,
        )

        self.assertEqual(
            record.document_type,
            DocumentType.TASK_SPECIFIC_HSE_TRAINING,
        )
        self.assertEqual(record.training_subject, "Working at Height")
        self.assertEqual(record.duration_text, "1 hour")
        self.assertEqual(record.metadata, {})

    def test_from_dict_parses_fields(self) -> None:
        record = TrainingRecord.from_dict(
            {
                "training_subject": "Manual Handling",
                "trainer": "Safety Team",
                "date": "28-04-2025",
                "duration": "45 minutes",
                "confidence": "0.82",
            },
            document_type="Task Specific HSE Training",
        )

        self.assertEqual(
            record.document_type,
            DocumentType.TASK_SPECIFIC_HSE_TRAINING,
        )
        self.assertEqual(record.date, date(2025, 4, 28))
        self.assertEqual(record.duration_text, "45 minutes")
        self.assertEqual(record.confidence, 0.82)

    def test_to_dict_serializes_record(self) -> None:
        record = TrainingRecord(
            document_type=DocumentType.TOOLBOX_TALK,
            training_subject="Heat Stress",
            trainer=None,
            date=date(2025, 5, 1),
            duration_text=None,
            confidence=None,
            metadata={"source": "unit-test"},
        )

        data = record.to_dict()

        self.assertEqual(data["document_type"], "Toolbox Talk")
        self.assertEqual(data["date"], "2025-05-01")
        self.assertEqual(data["metadata"], {"source": "unit-test"})
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_optional_fields(self) -> None:
        record = TrainingRecord.from_dict(
            {
                "training_subject": "",
                "trainer": None,
                "date": "not a date",
                "duration_text": None,
                "confidence": "not a number",
            },
            document_type=None,
        )

        self.assertEqual(record.document_type, DocumentType.UNKNOWN)
        self.assertIsNone(record.training_subject)
        self.assertIsNone(record.trainer)
        self.assertIsNone(record.date)
        self.assertIsNone(record.duration_text)
        self.assertIsNone(record.confidence)

    def test_str_returns_summary(self) -> None:
        record = TrainingRecord.from_dict(
            {
                "training_subject": "Emergency Response",
                "trainer": "HSE Lead",
                "date": "2025-06-10",
            },
            document_type=DocumentType.EMERGENCY_DRILL,
        )

        summary = str(record)

        self.assertIn("Emergency Drill", summary)
        self.assertIn("Emergency Response", summary)
        self.assertIn("2025-06-10", summary)


if __name__ == "__main__":
    unittest.main()
