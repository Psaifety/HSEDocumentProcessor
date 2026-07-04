<file name=ai/ai_engine.py path=/Users/praxsenghani/Projects/HistoricTrainingRecords/ai/ai_engine.py>TRAINING_RECORD_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {"type": "string"},
        "training_subject": {"type": "string"},
        "trainer": {"type": "string"},
        "date": {"type": "string", "format": "date"},
        "duration": {"type": "string"},
        "number_of_attendees": {"type": "integer"},
        "hazard_category": {"type": "string"},
        "confidence": {"type": ["number", "null"]},
        # other fields...
    },
    "required": [
        "document_type",
        "training_subject",
        "trainer",
        "date",
        "duration",
        "number_of_attendees",
        "hazard_category",
        "confidence",
    ],
    "additionalProperties": True,
}
</file>

<file name=models/training_record.py path=/Users/praxsenghani/Projects/HistoricTrainingRecords/models/training_record.py>import re

class TrainingRecord:
    # existing code...

    @staticmethod
    def _parse_hazard_category(value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        # Normalize repeated whitespace to single spaces
        normalized = re.sub(r'\s+', ' ', trimmed)
        return normalized

    @staticmethod
    def _normalise_trainer_name(value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        # Collapse repeated whitespace
        collapsed = re.sub(r'\s+', ' ', trimmed)
        # Remove spaces immediately after initials like "P. B." -> "P.B."
        normalized = re.sub(r'(\b[A-Z]\.)\s+(?=[A-Z]\.)', r'\1', collapsed)
        return normalized

    @classmethod
    def from_dict(cls, data: dict, document_type: DocumentType) -> TrainingRecord:
        # existing parsing logic...
        trainer_raw = data.get("trainer")
        trainer = cls._normalise_trainer_name(trainer_raw)
        # use trainer in creating TrainingRecord instance
        # rest of from_dict code unchanged except using normalized trainer
</file>

<file name=exporters/excel_exporter.py path=/Users/praxsenghani/Projects/HistoricTrainingRecords/exporters/excel_exporter.py>from openpyxl.styles import PatternFill

# existing code...

def export_training_records_to_excel(records: list[TrainingRecord], filename: str) -> None:
    # existing setup code...

    # Define fills for confidence highlighting
    light_red_fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
    light_amber_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

    for row_idx, record in enumerate(records, start=2):
        # existing code to write columns...

        # Write hazard_category column (new field)
        hazard_category = record.hazard_category
        worksheet.cell(row=row_idx, column=hazard_category_col_index, value=hazard_category)

        # Apply confidence fill if confidence exists
        confidence = record.confidence
        if confidence is not None:
            cell = worksheet.cell(row=row_idx, column=confidence_col_index)
            if confidence < 0.60:
                cell.fill = light_red_fill
            elif confidence < 0.80:
                cell.fill = light_amber_fill
        # rest of loop unchanged

    # existing save code...
</file>
