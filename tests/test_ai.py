import base64
import json
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from ai.ai_engine import (
    AIExtractionEngine,
    ImageInputError,
    InvalidAIResponseError,
    MissingAPIKeyError,
    TrainingExtraction,
)
from ai.prompt_loader import PromptLoader, PromptNotFoundError
from ai.response_logger import ResponseLogger
from config.settings import DEFAULT_MODEL, load_settings


@dataclass
class FakeSettings:
    openai_api_key: str | None
    openai_model: str
    project_root: Path
    prompts_dir: Path
    ai_log_dir: Path


class FakeResponse:
    id = "resp_test"
    usage = {"input_tokens": 10, "output_tokens": 20}

    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeResponsesClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return self.response


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.responses = FakeResponsesClient(response)


class AILayerTests(unittest.TestCase):
    def test_load_settings_reads_config_env(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            env_file = root / "config" / ".env"
            env_file.parent.mkdir()
            env_file.write_text(
                "OPENAI_API_KEY=test-key\nOPENAI_MODEL=custom-model\n",
                encoding="utf-8",
            )

            with patch.dict("os.environ", {}, clear=True):
                settings = load_settings(env_file, override=True, project_root=root)

        self.assertEqual(settings.openai_api_key, "test-key")
        self.assertEqual(settings.openai_model, "custom-model")
        self.assertEqual(settings.prompts_dir, root / "prompts")
        self.assertEqual(settings.ai_log_dir, root / "logs" / "ai")

    def test_load_settings_uses_default_model_without_env(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            with patch.dict("os.environ", {}, clear=True):
                settings = load_settings(root / "missing.env", project_root=root)

        self.assertIsNone(settings.openai_api_key)
        self.assertEqual(settings.openai_model, DEFAULT_MODEL)

    def test_prompt_loader_reads_markdown_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            prompts_dir = root / "prompts"
            prompts_dir.mkdir()
            prompt_file = prompts_dir / "task_specific_training.md"
            prompt_file.write_text("# Prompt\n\nExtract fields.", encoding="utf-8")

            loader = PromptLoader(prompts_dir)

            self.assertEqual(
                loader.load("task_specific_training"),
                "# Prompt\n\nExtract fields.",
            )
            self.assertEqual(
                loader.load("task_specific_training.md"),
                "# Prompt\n\nExtract fields.",
            )

    def test_prompt_loader_blocks_paths_outside_prompt_dir(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            loader = PromptLoader(Path(directory) / "prompts")

            with self.assertRaises(ValueError):
                loader.resolve("../outside")

    def test_prompt_loader_raises_for_missing_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            loader = PromptLoader(Path(directory) / "prompts")

            with self.assertRaises(PromptNotFoundError):
                loader.load("missing_prompt")

    def test_ai_engine_sends_image_input_and_parses_response(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            settings = _fake_settings(root)
            prompt_loader = _prompt_loader(root, "Extract training fields.")
            response_logger = ResponseLogger(root / "logs" / "ai")
            fake_client = FakeClient(
                FakeResponse(
                    json.dumps(
                        {
                            "training_subject": "Working at Height",
                            "trainer": "A. Trainer",
                            "date": "2025-04-28",
                            "duration": "1 hour",
                        }
                    )
                )
            )
            image_path = _image_file(root)

            engine = AIExtractionEngine(
                settings=settings,
                client=fake_client,
                prompt_loader=prompt_loader,
                response_logger=response_logger,
            )

            result = engine.extract_training_record(
                image_path,
                metadata={"source": "unit-test"},
            )

            self.assertEqual(
                result,
                TrainingExtraction(
                    training_subject="Working at Height",
                    trainer="A. Trainer",
                    date="2025-04-28",
                    duration="1 hour",
                ),
            )

            payload = fake_client.responses.last_kwargs
            self.assertEqual(payload["model"], "gpt-5.5")
            self.assertEqual(payload["text"]["format"]["type"], "json_schema")
            self.assertIs(payload["text"]["format"]["strict"], True)

            content = payload["input"][0]["content"]
            self.assertEqual(
                content[0],
                {"type": "input_text", "text": "Extract training fields."},
            )
            self.assertEqual(content[1]["type"], "input_image")
            self.assertTrue(content[1]["image_url"].startswith("data:image/png;base64,"))

            encoded_image = content[1]["image_url"].split(",", maxsplit=1)[1]
            self.assertTrue(base64.b64decode(encoded_image))

            log_records = _read_jsonl(root / "logs" / "ai" / "responses.jsonl")
            self.assertEqual(log_records[0]["response_id"], "resp_test")
            self.assertEqual(
                log_records[0]["parsed_output"]["training_subject"],
                "Working at Height",
            )
            self.assertNotIn("image_url", json.dumps(log_records[0]))

    def test_ai_engine_generic_extract_returns_dict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fake_client = FakeClient(
                FakeResponse(
                    json.dumps(
                        {
                            "training_subject": "Manual Handling",
                            "trainer": "Safety Team",
                            "date": None,
                            "duration": None,
                        }
                    )
                )
            )
            engine = AIExtractionEngine(
                settings=_fake_settings(root),
                client=fake_client,
                prompt_loader=_prompt_loader(root, "Extract fields."),
                response_logger=ResponseLogger(root / "logs" / "ai"),
            )

            result = engine.extract(
                document_type="Task Specific HSE Training",
                image=_image_file(root),
            )

            self.assertEqual(result["training_subject"], "Manual Handling")
            self.assertEqual(result["trainer"], "Safety Team")

            log_records = _read_jsonl(root / "logs" / "ai" / "responses.jsonl")
            self.assertEqual(
                log_records[0]["metadata"]["document_type"],
                "Task Specific HSE Training",
            )

    def test_ai_engine_accepts_pillow_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fake_client = FakeClient(
                FakeResponse(
                    json.dumps(
                        {
                            "training_subject": None,
                            "trainer": None,
                            "date": None,
                            "duration": None,
                        }
                    )
                )
            )
            engine = AIExtractionEngine(
                settings=_fake_settings(root),
                client=fake_client,
                prompt_loader=_prompt_loader(root, "Extract fields."),
                response_logger=ResponseLogger(root / "logs" / "ai"),
            )

            engine.extract_training_record(Image.new("RGB", (1, 1), color="white"))

            image_url = fake_client.responses.last_kwargs["input"][0]["content"][1][
                "image_url"
            ]
            self.assertTrue(image_url.startswith("data:image/png;base64,"))

    def test_ai_engine_rejects_missing_image_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            engine = AIExtractionEngine(
                settings=_fake_settings(root),
                client=FakeClient(FakeResponse("{}")),
                prompt_loader=_prompt_loader(root, "Extract fields."),
                response_logger=ResponseLogger(root / "logs" / "ai"),
            )

            with self.assertRaises(ImageInputError):
                engine.extract_training_record(root / "missing.png")

    def test_ai_engine_raises_missing_api_key_without_client(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            engine = AIExtractionEngine(
                settings=FakeSettings(
                    openai_api_key=None,
                    openai_model="gpt-5.5",
                    project_root=root,
                    prompts_dir=root / "prompts",
                    ai_log_dir=root / "logs" / "ai",
                ),
                prompt_loader=_prompt_loader(root, "Extract fields."),
                response_logger=ResponseLogger(root / "logs" / "ai"),
            )

            with self.assertRaises(MissingAPIKeyError):
                engine.extract_training_record(_image_file(root))

            error_records = _read_jsonl(root / "logs" / "ai" / "errors.jsonl")
            self.assertEqual(error_records[0]["error_type"], "MissingAPIKeyError")

    def test_ai_engine_raises_and_logs_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            engine = AIExtractionEngine(
                settings=_fake_settings(root),
                client=FakeClient(FakeResponse("not json")),
                prompt_loader=_prompt_loader(root, "Extract fields."),
                response_logger=ResponseLogger(root / "logs" / "ai"),
            )

            with self.assertRaises(InvalidAIResponseError):
                engine.extract_training_record(_image_file(root))

            error_records = _read_jsonl(root / "logs" / "ai" / "errors.jsonl")
            self.assertEqual(error_records[0]["response_id"], "resp_test")
            self.assertEqual(error_records[0]["error_type"], "InvalidAIResponseError")


def _fake_settings(root: Path) -> FakeSettings:
    return FakeSettings(
        openai_api_key="test-key",
        openai_model="gpt-5.5",
        project_root=root,
        prompts_dir=root / "prompts",
        ai_log_dir=root / "logs" / "ai",
    )


def _prompt_loader(root: Path, prompt_text: str) -> PromptLoader:
    prompts_dir = root / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    (prompts_dir / "task_specific_training.md").write_text(
        prompt_text,
        encoding="utf-8",
    )
    return PromptLoader(prompts_dir)


def _image_file(root: Path) -> Path:
    image_path = root / "record.png"
    Image.new("RGB", (1, 1), color="white").save(image_path)
    return image_path


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


if __name__ == "__main__":
    unittest.main()
