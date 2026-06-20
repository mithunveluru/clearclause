from app.core.config import settings
from app.ocr.base import OCRProvider
from app.ocr.paddle import PaddleOCRProvider
from app.ocr.tesseract import TesseractOCRProvider

_PROVIDERS: dict[str, type[OCRProvider]] = {
    "tesseract": TesseractOCRProvider,
    "paddle": PaddleOCRProvider,
}


def get_ocr_provider(name: str | None = None) -> OCRProvider:
    key = (name or settings.OCR_PROVIDER).lower()
    try:
        return _PROVIDERS[key]()
    except KeyError:
        raise ValueError(f"Unknown OCR provider: {key}")
