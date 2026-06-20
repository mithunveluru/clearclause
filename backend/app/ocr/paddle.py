from app.ocr.base import OCRProvider


class PaddleOCRProvider(OCRProvider):
    """Placeholder adapter for harder layouts (future upgrade per spec §12).

    Not implemented in the MVP. The abstraction exists so swapping providers
    is a config change (OCR_PROVIDER=paddle), not a code change in callers.
    """

    def extract(self, file_path: str) -> list[dict]:
        raise NotImplementedError(
            "PaddleOCR adapter is not implemented yet; set OCR_PROVIDER=tesseract"
        )
