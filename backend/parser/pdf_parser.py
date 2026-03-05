"""
PDF Resume Parser using pdfplumber + OCR fallback.
- Normal PDFs: pdfplumber (fast)
- Scanned/image PDFs: pytesseract OCR (fallback)
"""

import logging
import pytesseract
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image

logger = logging.getLogger(__name__)

# Paths for Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH   = r"C:\Program Files\poppler\bin"

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def _extract_with_pdfplumber(file_path: str) -> str:
    """Try normal text extraction first."""
    try:
        full_text = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text.append(text)
                else:
                    logger.warning(f"Page {i+1} returned no text.")
        return "\n".join(full_text)
    except Exception as e:
        logger.error(f"pdfplumber failed: {e}")
        return ""


def _extract_with_ocr(file_path: str) -> str:
    """
    OCR fallback for scanned/image-based PDFs.
    Converts each page to image → runs tesseract → extracts text.
    """
    try:
        logger.info("Falling back to OCR for scanned PDF...")
        images = convert_from_path(
            file_path,
            dpi=300,
            poppler_path=POPPLER_PATH
        )

        full_text = []
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang="eng")
            if text.strip():
                full_text.append(text)
                logger.info(f"OCR page {i+1}: {len(text)} characters extracted.")
            else:
                logger.warning(f"OCR page {i+1}: no text found.")

        return "\n".join(full_text)

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        raise ValueError("Failed to extract text via OCR. Check Tesseract and Poppler installation.")


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file.

    Strategy:
      1. Try pdfplumber (fast, normal PDFs)
      2. If less than 200 chars → fallback to OCR (scanned PDFs)

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If no text could be extracted.
    """
    try:
        # Step 1: Try normal extraction
        text = _extract_with_pdfplumber(file_path)

        # Step 2: If text is good enough → return it
        if text.strip() and len(text.strip()) > 200:
            logger.info(f"PDF parsed with pdfplumber: {len(text)} characters.")
            return text

        # Step 3: Fallback to OCR
        logger.info("pdfplumber returned insufficient text — trying OCR...")
        text = _extract_with_ocr(file_path)

        if not text.strip():
            raise ValueError("No text extracted from PDF even after OCR.")

        logger.info(f"PDF parsed with OCR: {len(text)} characters.")
        return text

    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        raise
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to parse PDF '{file_path}': {e}")
        raise