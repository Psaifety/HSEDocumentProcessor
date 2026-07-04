import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pdf2image import convert_from_path
from PIL import ImageDraw

# CHANGE IF REQUIRED
PDF_FILE = Path(
    "/Users/praxsenghani/Desktop/Al Nasr Training Files/001 April 2025/Trainings/28-04-25.pdf"
)

page = convert_from_path(
    PDF_FILE,
    dpi=300
)[0]

draw = ImageDraw.Draw(page)

width, height = page.size

print(f"Image Size : {width} x {height}")

# -------------------------------------------------
# TEMPORARY REGIONS
# (We'll fine tune these together)
# -------------------------------------------------

subject = (
    250,
    250,
    width-200,
    430
)

trainer = (
    250,
    430,
    900,
    560
)

date = (
    900,
    430,
    1400,
    560
)

duration = (
    1400,
    430,
    width-200,
    560
)

attendees = (
    180,
    560,
    width-180,
    height-250
)

regions = [
    subject,
    trainer,
    date,
    duration,
    attendees
]

for region in regions:
    draw.rectangle(
        region,
        outline="red",
        width=5
    )

page.save("tests/document_regions.png")

print()

print("Saved")

print("tests/document_regions.png")