from pathlib import Path

from pdf2image import convert_from_path

# CHANGE THIS TO ONE OF YOUR PDFs
PDF_FILE = Path(
    "/Users/praxsenghani/Desktop/Al Nasr Training Files/001 April 2025/Trainings/28-04-25.pdf"
)

pages = convert_from_path(PDF_FILE)

print(f"Pages: {len(pages)}")

pages[0].show()