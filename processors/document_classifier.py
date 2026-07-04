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

        if "DAILY PRE-START BRIEFING" in text:
            return "Activity Briefing"

        if "EMERGENCY EVACUATION" in text:
            return "Emergency Drill"

        if "TOOLBOX TALK" in text:
            return "Toolbox Talk"

        if "INDUCTION" in text:
            return "Induction"

        if "TRAINING ATTENDANCE SHEET" in text:
            return "Task Specific HSE Training"

        if "CAMPAIGN" in text:
            return "HSE Campaign"

        return "Unknown"