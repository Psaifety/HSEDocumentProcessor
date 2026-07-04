import sys

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytesseract
from pdf2image import convert_from_path

from processors.image_processor import ImageProcessor

# CHANGE THIS TO ANY TRAINING RECORD
PDF_FILE = Path(
    "/Users/praxsenghani/Desktop/Al Nasr Training Files/001 April 2025/Trainings/28-04-25.pdf"
)

print("Reading PDF...")

pages = convert_from_path(
    PDF_FILE,
    dpi=300
)

page = pages[0]

print("Enhancing image...")

page = ImageProcessor.enhance(page)

print("Running OCR...")

text = pytesseract.image_to_string(
    page,
    lang="eng",
    config="--psm 6"
)

print()

print("=" * 80)

print(text)

print("=" * 80)

# Save the enhanced image so you can inspect it
page.save("tests/enhanced_page.png")

print()
print("Enhanced image saved to tests/enhanced_page.png")