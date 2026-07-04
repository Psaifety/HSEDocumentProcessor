import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from processors.document_classifier import DocumentClassifier

classifier = DocumentClassifier()

PDF_FILE = Path(
    "/Users/praxsenghani/Desktop/Al Nasr Training Files/001 April 2025/Trainings/28-04-25.pdf"
)

doc_type = classifier.classify(PDF_FILE)

print()
print("=" * 40)
print("Document Type")
print("=" * 40)
print(doc_type)
print("=" * 40)