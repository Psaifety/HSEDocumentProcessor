"""
Live integration test for the BatchPipeline.

Processes every PDF in the configured sample folder and prints a
summary of the results.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from processors.batch_pipeline import BatchPipeline
from exporters.excel_exporter import ExcelExporter
from datetime import datetime


def main() -> None:

    load_dotenv("config/.env")

    folder = os.getenv("SAMPLE_TRAINING_FOLDER")

    if not folder:
        print(
            "SAMPLE_TRAINING_FOLDER is not configured "
            "in config/.env"
        )
        return

    folder = Path(folder)

    print("=" * 60)
    print("Historic Training Records")
    print("Batch Processing")
    print("=" * 60)
    print()

    pipeline = BatchPipeline()

    result = pipeline.process_folder(folder)

    output_folder = Path("output")
    output_folder.mkdir(exist_ok=True)

    output_file = (
        output_folder
        / f"HSE_Training_Register_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    )

    ExcelExporter().export(result, output_file)

    print()
    print(f"Excel workbook saved to: {output_file.resolve()}")

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    print(f"Documents Found      : {result.total_documents}")
    print(f"Successful           : {result.successful_documents}")
    print(f"Failed               : {result.failed_documents}")
    print(f"Success Rate         : {result.success_rate}%")
    print(f"Processing Time      : {result.processing_time_seconds:.2f}s")
    print(
        f"Average / Document   : "
        f"{result.average_processing_time:.2f}s"
    )

    print()
    print("=" * 60)
    print("Training Records")
    print("=" * 60)

    for processing_result in result.results:

        if processing_result.success:

            print(processing_result.training_record)

        else:

            print(
                f"FAILED : "
                f"{processing_result.pdf_path.name}"
            )

            print(
                f"Reason : "
                f"{processing_result.error_message}"
            )

        print("-" * 60)


if __name__ == "__main__":
    main()