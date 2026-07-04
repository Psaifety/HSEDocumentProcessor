from PIL import Image, ImageEnhance, ImageFilter


class ImageProcessor:

    @staticmethod
    def enhance(image: Image.Image) -> Image.Image:
        """
        Enhance a scanned training record for OCR.
        """

        # Convert to greyscale
        image = image.convert("L")

        # Increase contrast
        image = ImageEnhance.Contrast(image).enhance(2.0)

        # Sharpen text
        image = image.filter(ImageFilter.SHARPEN)

        # Convert to pure black & white
        image = image.point(lambda p: 255 if p > 160 else 0)

        return image