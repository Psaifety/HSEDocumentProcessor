from pathlib import Path

TRAINING_TYPE_MAP = {
    "trainings": "Toolbox Talk",
    "training": "Toolbox Talk",

    "inductions": "Induction",
    "induction": "Induction",
    "hse induction": "Induction",

    "hse campaign": "HSE Campaign",
    "campaign": "HSE Campaign",

    "pre-start briefing": "Activity Briefing",
    "pre start briefing": "Activity Briefing",
    "prestart briefing": "Activity Briefing",

    "hse drill": "Emergency Drill",
    "drill": "Emergency Drill",

    "hse training": "Task Specific HSE Training",
}


class FolderScanner:

    def __init__(self, root_folder):
        self.root_folder = Path(root_folder)

    def scan(self):

        results = []

        for month in sorted(self.root_folder.iterdir()):

            if not month.is_dir():
                continue

            month_result = {
                "month": month.name,
                "folders": []
            }

            for folder in sorted(month.iterdir()):

                if not folder.is_dir():
                    continue

                folder_name = folder.name.lower()

                training_type = "Unknown"

                for key, value in TRAINING_TYPE_MAP.items():

                    if key in folder_name:
                        training_type = value
                        break

                pdf_count = len(list(folder.glob("*.pdf")))

                month_result["folders"].append({
                    "folder": folder.name,
                    "type": training_type,
                    "pdfs": pdf_count
                })

            results.append(month_result)

        return results