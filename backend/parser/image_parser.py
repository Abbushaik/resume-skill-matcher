"""
Image Resume Parser using pytesseract OCR.
Supports JPG, JPEG, PNG, BMP, TIFF image formats.
"""

import logging
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Tesseract path for Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image file using OCR.

    Supports: JPG, JPEG, PNG, BMP, TIFF

    Args:
        file_path: Path to the image file.

    Returns:
        Extracted text as a single string.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If no text could be extracted.
    """
    try:
        image = Image.open(file_path)

        # Convert to RGB if needed (handles PNG with alpha channel)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        # Run OCR
        text = pytesseract.image_to_string(image, lang="eng")

        if not text.strip():
            raise ValueError(
                "No text extracted from image. "
                "Make sure the image is clear and not blurry."
            )

        logger.info(f"Image parsed with OCR: {len(text)} characters extracted.")
        return text

    except FileNotFoundError:
        logger.error(f"Image file not found: {file_path}")
        raise
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to parse image '{file_path}': {e}")
        raise