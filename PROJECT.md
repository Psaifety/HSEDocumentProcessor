# Historic Training Records

## Vision

Historic Training Records converts historic HSE training records into structured digital data using AI. The application is designed to process large archives of scanned training PDFs, extract reliable record data with GPT-5.5 Vision, and prepare clean outputs for validation and Excel export.

Primary goals:

- Process thousands of scanned PDFs
- Use GPT-5.5 Vision
- Produce clean structured records
- Export to Excel
- Support multiple HSE document types

---

## Current Architecture

```text
GUI
↓
DocumentPipeline
↓
DocumentClassifier
↓
PDFProcessor
↓
AIEngine
↓
GPT-5.5
↓
ProcessingResult
```

---

## Completed Features

- Application Shell
- Folder Scanner
- OCR Engine
- Document Classification
- AI Engine
- Document Processing Pipeline

---

## Planned Features

- TrainingRecord model
- Validation Engine
- Batch Processing
- Excel Export
- GUI Integration
- Progress Reporting
- Manual Review Screen

---

## Folder Structure

- `ai/`: OpenAI Responses API integration, prompt loading, and AI response logging.
- `assets/`: Static project assets used by the application.
- `config/`: Runtime configuration, environment loading, and local `.env` settings.
- `exporters/`: Future Excel and structured data export modules.
- `logs/`: Runtime logs generated during processing.
- `models/`: Dataclasses and structured domain/result models.
- `processors/`: Folder scanning, OCR/image helpers, PDF rendering, classification, and pipeline orchestration.
- `prompts/`: Markdown prompts used by AI extraction.
- `tests/`: Unit, smoke, and integration test scripts.
- `ui/`: CustomTkinter application shell and future GUI integration.

---

## Coding Standards

- Python 3.14
- Use `pathlib` for filesystem paths
- Add type hints
- Add docstrings
- Avoid hardcoded paths
- Keep a modular architecture
- Keep one responsibility per class

---

## Running Tests

Run tests as modules from the project root:

```bash
python -m tests.test_xxx
```

Examples:

```bash
python -m tests.test_ai
python -m tests.test_pipeline
```

Prefer module execution over running test files directly so imports resolve consistently from the project root.

---

## Git

Generated files must never be committed, including:

- `__pycache__`
- `*.pyc`
- `logs`
- Rendered images

Keep commits focused on source code, prompts, tests, and project documentation.
