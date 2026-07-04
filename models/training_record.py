"""Business model for an extracted training record."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Mapping

from models.document_type import DocumentType


@dataclass(frozen=True)
class TrainingRecord:
    """Strongly typed training record extracted from an HSE document."""

    document_type: DocumentType
    training_subject: str | None
    trainer: str | None
    date: date | None
    duration_text: str | None
    number_of_attendees: int | None = None
    hazard_category: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
        *,
        document_type: DocumentType | str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "TrainingRecord":
        """Create a training record from extracted AI data."""

        raw_metadata = data.get("metadata")
        record_metadata = dict(raw_metadata) if isinstance(raw_metadata, Mapping) else {}

        if metadata:
            record_metadata.update(dict(metadata))

        return cls(
            document_type=DocumentType.from_value(
                document_type or data.get("document_type")
            ),
            training_subject=_optional_string(data.get("training_subject")),
            trainer=_optional_string(data.get("trainer")),
            date=_parse_date(data.get("date")),
            duration_text=_optional_string(
                data.get("duration_text", data.get("duration"))
            ),
            number_of_attendees=_parse_int(
                data.get("number_of_attendees")
                or data.get("attendee_count")
            ),
            hazard_category=_parse_hazard_category(
                data.get("hazard_category")
                or data.get("hazard_categories")
            ),
            confidence=_parse_confidence(data.get("confidence")),
            metadata=record_metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the training record."""

        return {
            "document_type": self.document_type.value,
            "training_subject": self.training_subject,
            "trainer": self.trainer,
            "date": self.date.isoformat() if self.date else None,
            "duration_text": self.duration_text,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "number_of_attendees": self.number_of_attendees,
            "hazard_category": self.hazard_category,
        }

    def __str__(self) -> str:
        """Return a concise human-readable summary of the record."""

        subject = self.training_subject or "Unknown subject"
        trainer = self.trainer or "Unknown trainer"
        record_date = self.date.isoformat() if self.date else "Unknown date"
        attendees = (
            str(self.number_of_attendees)
            if self.number_of_attendees is not None else "Unknown"
        )
        return (
            f"{self.document_type.value}: {subject} | "
            f"Trainer: {trainer} | "
            f"Date: {record_date} | "
            f"Attendees: {attendees}"
        )
        


def _optional_string(value: Any) -> str | None:
    """Return a stripped string or ``None`` for blank/non-string values."""

    if value is None:
        return None

    if not isinstance(value, str):
        return None

    stripped = value.strip()
    return stripped or None


def _parse_confidence(value: Any) -> float | None:
    """Parse a confidence value from AI output."""

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, int | float):
        return float(value)

    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None

    return None

def _parse_int(value: Any) -> int | None:
    """Parse an integer value."""

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None

    return None

def _parse_hazard_category(value: Any) -> str | None:
    """Return a single hazard category."""

    if value is None:
        return None

    if isinstance(value, str):
        text = value.strip()
        return text or None

    if isinstance(value, list):
        for item in value:
            text = str(item).strip()
            if text:
                return text
        return None

    text = str(value).strip()
    return text or None


def _parse_date(value: Any) -> date | None:
    """Parse common date representations into ``datetime.date``."""

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    text = value.strip()

    if not text:
        return None

    for date_format in (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d-%m-%y",
        "%d/%m/%y",
        "%d.%m.%y",
        "%d %b %Y",
        "%d %B %Y",
        "%d %b %y",
    ):
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue

    try:
        return date.fromisoformat(text)
    except ValueError:
        return None
