"""Document type definitions for classified HSE records."""

from __future__ import annotations

from enum import Enum


class DocumentType(str, Enum):
    """Known HSE document types produced by the classifier."""

    TASK_SPECIFIC_HSE_TRAINING = "Task Specific HSE Training"
    TOOLBOX_TALK = "Toolbox Talk"
    INDUCTION = "Induction"
    ACTIVITY_BRIEFING = "Activity Briefing"
    EMERGENCY_DRILL = "Emergency Drill"
    HSE_CAMPAIGN = "HSE Campaign"
    UNKNOWN = "Unknown"

    @classmethod
    def from_value(cls, value: "DocumentType | str | None") -> "DocumentType":
        """Return a document type enum for ``value``."""

        if isinstance(value, cls):
            return value

        if value is None:
            return cls.UNKNOWN

        normalized = str(value).strip()

        for document_type in cls:
            if document_type.value.casefold() == normalized.casefold():
                return document_type

        return cls.UNKNOWN
