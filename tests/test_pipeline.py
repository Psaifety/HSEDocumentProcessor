"""Live integration script for the document processing pipeline.

This file is import-safe: the pipeline runs only when executed directly.
It reads SAMPLE_TRAINING_PDF from config/.env.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import load_settings  # noqa: E402
from processors.document_pipeline import DocumentPipeline  # noqa: E402

SAMPLE_PDF_ENV_VAR = "SAMPLE_TRAINING_PDF"


def main() -> int:
    """Run the live document pipeline against the configured sample PDF."""

    settings = load_settings(override=True)
    sample_pdf = os.getenv(SAMPLE_PDF_ENV_VAR)

    if not sample_pdf:
        print(
            f"{SAMPLE_PDF_ENV_VAR} is not configured. Add it to config/.env "
            "to run the live pipeline integration test."
        )
        return 0

    if not settings.openai_api_key:
        print(
            "OPENAI_API_KEY is not configured. Add it to config/.env to run "
            "the live pipeline integration test."
        )
        return 0

    pdf_path = Path(sample_pdf).expanduser().resolve()
    start_time = perf_counter()

    result = DocumentPipeline().process(pdf_path)
    total_processing_time = perf_counter() - start_time

    print(json.dumps(result.to_dict(), indent=4, ensure_ascii=False))
    print(f"\nTotal processing time: {total_processing_time:.2f} seconds")

    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
