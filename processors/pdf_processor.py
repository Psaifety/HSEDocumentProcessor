"""Reusable PDF rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image


@dataclass(frozen=True)
class RenderedPage:
    """Rendered PDF page image and optional saved image path."""

    image: Image.Image
    image_path: Path | None = None


class PDFProcessor:
    """Render PDF pages into images for downstream processing."""

    def __init__(self, *, dpi: int = 300, output_dir: Path | str | None = None) -> None:
        self.dpi = dpi
        self.output_dir = Path(output_dir) if output_dir else None

    def render_first_page(self, pdf_path: Path | str) -> RenderedPage:
        """Render the first page of ``pdf_path`` as a Pillow image."""

        path = Path(pdf_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"PDF file does not exist: {path}")

        pages = convert_from_path(
            path,
            dpi=self.dpi,
            first_page=1,
            last_page=1,
        )

        if not pages:
            raise ValueError(f"No pages were rendered from PDF: {path}")

        image = pages[0]
        image_path = self._save_rendered_image(path, image)

        return RenderedPage(image=image, image_path=image_path)

    def _save_rendered_image(self, pdf_path: Path, image: Image.Image) -> Path | None:
        """Save a rendered page when an output directory was configured."""

        if self.output_dir is None:
            return None

        self.output_dir.mkdir(parents=True, exist_ok=True)
        image_path = self.output_dir / f"{pdf_path.stem}_page_1.png"
        image.save(image_path)
        return image_path
