from pathlib import Path

import pytesseract
from pdf2image import convert_from_path


class DocumentClassifier:

    def classify(self, pdf_path: Path) -> str:
        """
        Returns one of:

        Task Specific HSE Training
        Toolbox Talk
        Induction
        Activity Briefing
        Emergency Drill
        HSE Campaign
        Unknown
        """

        page = convert_from_path(
            pdf_path,
            dpi=200,
            first_page=1,
            last_page=1
        )[0]

        text = pytesseract.image_to_string(page).upper()

        normalized = (
            text.replace("-", " ")
                .replace("—", " ")
                .replace("_", " ")
                .replace("/", " ")
                .replace("\n", " ")
                .replace("\r", " ")
        )

        normalized = " ".join(normalized.split())

        print("=" * 80)
        print(pdf_path.name)
        print(text[:1500])   # first 1500 characters
        print("=" * 80)

        if (
            "PRE START" in normalized
            and "BRIEFING" in normalized
        ):
            return "Activity Briefing"

        if "EMERGENCY EVACUATION" in normalized:
            return "Emergency Drill"

        if (
            "TOOLBOX" in normalized
            and "TALK" in normalized
        ):
             return "Toolbox Talk"

        if "INDUCTION" in normalized:
            return "Induction"

        if (
            "TRAINING" in normalized
            and "ATTENDANCE" in normalized
        ):
            return "Task Specific HSE Training"

        if "CAMPAIGN" in normalized:
            return "HSE Campaign"

        print()
        print("=" * 80)
        print("UNKNOWN DOCUMENT")
        print(pdf_path.name)
        print()
        print(normalized[:500])
        print("=" * 80)
        print()

        return "Unknown"