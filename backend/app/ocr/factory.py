from app.core.config import settings
from app.ocr.base import OCRProvider
from app.ocr.tesseract import TesseractOCRProvider


def get_ocr_provider(name: str | None = None) -> OCRProvider:
    key = (name or settings.OCR_PROVIDER).lower()
    if key == "tesseract":
        return TesseractOCRProvider()
    raise ValueError(f"Unknown OCR provider: {key}")
