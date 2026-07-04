"""Live GPT-5.5 integration check for the AI extraction engine.

This file is intentionally import-safe: it performs the live API call only when
executed directly, so it does not affect the existing unit test suite.

Usage:
    python tests/test_ai_live.py /path/to/sample-training.pdf

Alternatively, set SAMPLE_TRAINING_PDF in config/.env.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from pdf2image import convert_from_path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai import AIExtractionEngine  # noqa: E402
from config.settings import load_settings  # noqa: E402

SAMPLE_PDF_ENV_VAR = "SAMPLE_TRAINING_PDF"


def main() -> int:
    """Run a live extraction against GPT-5.5 and print the returned JSON."""

    settings = load_settings(override=True)

    if not settings.openai_api_key:
        print(
            "OPENAI_API_KEY is not configured. Add it to config/.env to run "
            "the live AI integration test."
        )
        return 0

    pdf_path = _get_sample_pdf_path()

    if pdf_path is None:
        print(
            "No sample training PDF was provided. Pass a PDF path as the first "
            f"argument, or set {SAMPLE_PDF_ENV_VAR} in config/.env."
        )
        return 0

    if not pdf_path.exists() or not pdf_path.is_file():
        print(f"Sample training PDF not found: {pdf_path}")
        return 1

    print(f"Rendering first page: {pdf_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        pages = convert_from_path(
            pdf_path,
            dpi=300,
            first_page=1,
            last_page=1,
            output_folder=Path(temp_dir),
        )

        if not pages:
            print(f"No pages were rendered from: {pdf_path}")
            return 1

        print(f"Calling {settings.openai_model}...")

        engine = AIExtractionEngine(settings=settings)
        result = engine.extract_training_record(
            pages[0],
            metadata={"source_pdf": str(pdf_path)},
        )

    print(json.dumps(result.to_dict(), indent=4, ensure_ascii=False))
    return 0


def _get_sample_pdf_path() -> Path | None:
    """Return the sample PDF path from argv or config/.env."""

    if len(sys.argv) > 1 and sys.argv[1].strip():
        return Path(sys.argv[1]).expanduser().resolve()

    configured_path = os.getenv(SAMPLE_PDF_ENV_VAR)

    if configured_path:
        return Path(configured_path).expanduser().resolve()

    return None


if __name__ == "__main__":
    raise SystemExit(main())
