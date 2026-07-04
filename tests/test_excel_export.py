"""
Live integration test for the Excel exporter.
"""

from pathlib import Path
import os

from dotenv import load_dotenv

from exporters.excel_exporter import ExcelExporter
from processors.batch_pipeline import BatchPipeline


def main():

    load_dotenv("config/.env")

    folder = os.getenv("SAMPLE_TRAINING_FOLDER")

    if not folder:
        print("SAMPLE_TRAINING_FOLDER not configured.")
        return

    folder = Path(folder)

    output = Path.home() / "Desktop" / "training_records.xlsx"

    print("Processing documents...")

    batch = BatchPipeline().process_folder(folder)

    print("Exporting Excel workbook...")

    ExcelExporter().export(batch, output)

    print()
    print("=" * 60)
    print("Export complete!")
    print("=" * 60)
    print(output)


if __name__ == "__main__":
    main()