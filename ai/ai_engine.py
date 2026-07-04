"""OpenAI Responses API extraction engine."""

from __future__ import annotations

import base64
import json
import mimetypes
from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image

from ai.prompt_loader import PromptLoader
from ai.response_logger import ResponseLogger
from config.settings import Settings, load_settings


TRAINING_RECORD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "training_subject": {"type": ["string", "null"]},
        "trainer": {"type": ["string", "null"]},
        "date": {"type": ["string", "null"]},
        "duration": {"type": ["string", "null"]},
    },
    "required": [
        "training_subject",
        "trainer",
        "date",
        "duration",
    ],
}

TRAINING_RECORD_TEXT_FORMAT: dict[str, Any] = {
    "format": {
        "type": "json_schema",
        "name": "training_record_extraction",
        "schema": TRAINING_RECORD_SCHEMA,
        "strict": True,
    }
}


class AIExtractionError(Exception):
    """Base exception for AI extraction failures."""


class MissingAPIKeyError(AIExtractionError):
    """Raised when no OpenAI API key is available."""


class ImageInputError(AIExtractionError):
    """Raised when an image cannot be prepared for extraction."""


class APIRequestError(AIExtractionError):
    """Raised when the OpenAI API request fails."""


class InvalidAIResponseError(AIExtractionError):
    """Raised when the AI response cannot be parsed into expected data."""


@dataclass(frozen=True)
class TrainingExtraction:
    """Structured fields extracted from a training attendance sheet."""

    training_subject: str | None
    trainer: str | None
    date: str | None
    duration: str | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrainingExtraction":
        """Build a typed extraction result from model JSON."""

        return cls(
            training_subject=_optional_string(data.get("training_subject")),
            trainer=_optional_string(data.get("trainer")),
            date=_optional_string(data.get("date")),
            duration=_optional_string(data.get("duration")),
        )

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-serializable representation of the extraction."""

        return asdict(self)


class AIExtractionEngine:
    """Extract structured data from document images."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        client: Any | None = None,
        prompt_loader: PromptLoader | None = None,
        response_logger: ResponseLogger | None = None,
    ) -> None:
        self.settings = settings or load_settings()
        self.client = client
        self.prompt_loader = prompt_loader or PromptLoader(self.settings.prompts_dir)
        self.response_logger = response_logger or ResponseLogger(self.settings.ai_log_dir)

    def extract(
        self,
        document_type: str,
        image: Path | str | Image.Image,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Extract structured data from a document image.

        This generic entry point keeps callers decoupled from document-specific
        extraction methods. The current AI prompt/schema extracts the fields
        supported by the existing training-record engine.
        """

        extraction_metadata = {
            "document_type": document_type,
            **(metadata or {}),
        }
        extraction = self.extract_training_record(
            image,
            metadata=extraction_metadata,
        )
        return extraction.to_dict()

    def extract_training_record(
        self,
        image: Path | str | Image.Image,
        *,
        prompt_name: str = "task_specific_training",
        metadata: dict[str, Any] | None = None,
    ) -> TrainingExtraction:
        """Extract training fields from an image using the Responses API."""

        prompt = self.prompt_loader.load(prompt_name)
        image_url = self._image_to_data_url(image)

        try:
            client = self._get_client()
        except MissingAPIKeyError as exc:
            self.response_logger.log_error(
                model=self.settings.openai_model,
                prompt_name=prompt_name,
                error=exc,
                metadata=metadata,
            )
            raise

        try:
            response = client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {"type": "input_image", "image_url": image_url},
                        ],
                    }
                ],
                text=TRAINING_RECORD_TEXT_FORMAT,
            )
        except Exception as exc:
            wrapped = APIRequestError(f"OpenAI extraction request failed: {exc}")
            self.response_logger.log_error(
                model=self.settings.openai_model,
                prompt_name=prompt_name,
                error=wrapped,
                metadata=metadata,
            )
            raise wrapped from exc

        try:
            parsed = self._parse_response(response)
        except InvalidAIResponseError as exc:
            self.response_logger.log_error(
                model=self.settings.openai_model,
                prompt_name=prompt_name,
                error=exc,
                metadata=metadata,
                response_id=getattr(response, "id", None),
            )
            raise

        self.response_logger.log_success(
            model=self.settings.openai_model,
            prompt_name=prompt_name,
            response=response,
            parsed_output=parsed,
            metadata=metadata,
        )

        return parsed

    def _get_client(self) -> Any:
        """Return an OpenAI client, creating one lazily when needed."""

        if self.client is not None:
            return self.client

        if not self.settings.openai_api_key:
            raise MissingAPIKeyError("OPENAI_API_KEY is not configured.")

        from openai import OpenAI

        self.client = OpenAI(api_key=self.settings.openai_api_key)
        return self.client

    def _image_to_data_url(self, image: Path | str | Image.Image) -> str:
        """Encode an image path or Pillow image as a base64 data URL."""

        if isinstance(image, Image.Image):
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            return f"data:image/png;base64,{encoded}"

        image_path = Path(image)

        if not image_path.exists() or not image_path.is_file():
            raise ImageInputError(f"Image file does not exist: {image_path}")

        mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"

        if not mime_type.startswith("image/"):
            raise ImageInputError(f"File is not a supported image: {image_path}")

        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    @staticmethod
    def _parse_response(response: Any) -> TrainingExtraction:
        """Parse ``response.output_text`` into a typed extraction result."""

        output_text = getattr(response, "output_text", None)

        if not output_text:
            raise InvalidAIResponseError("OpenAI response did not include output_text.")

        try:
            data = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise InvalidAIResponseError("OpenAI response was not valid JSON.") from exc

        if not isinstance(data, dict):
            raise InvalidAIResponseError("OpenAI response JSON must be an object.")

        return TrainingExtraction.from_dict(data)


def _optional_string(value: Any) -> str | None:
    """Return ``value`` if it is a string, otherwise ``None``."""

    if value is None or isinstance(value, str):
        return value

    return None
