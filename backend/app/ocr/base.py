from abc import ABC, abstractmethod


class OCRProvider(ABC):
    """Pluggable OCR backend. Implementations return a flat list of text blocks.

    Each block is a dict:
        {
          "page_number": int,   # 1-based
          "block_order": int,   # reading order within the page, 0-based
          "text": str,
          "bbox": [x, y, w, h]  # pixel box on the rendered page, or None
        }
    """

    @abstractmethod
    def extract(self, file_path: str) -> list[dict]:
        ...
