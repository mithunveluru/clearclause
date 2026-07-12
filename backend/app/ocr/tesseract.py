from collections import OrderedDict

import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image
from pytesseract import Output

from app.core.config import settings
from app.ocr.base import OCRProvider


class TesseractOCRProvider(OCRProvider):
    """CPU-only OCR via Tesseract. PDFs are rasterized page-by-page first."""

    def __init__(self, dpi: int = 200):
        self.dpi = dpi

    def extract(self, file_path: str) -> list[dict]:
        blocks: list[dict] = []
        if file_path.lower().endswith(".pdf"):
            # One page at a time: an unbounded convert_from_path() holds every page
            # in memory simultaneously (~26MB/page at 200dpi) and OOMs the worker.
            # MAX_PDF_PAGES is enforced at upload; re-applied here as a backstop.
            pages = min(pdfinfo_from_path(file_path)["Pages"], settings.MAX_PDF_PAGES)
            for page_number in range(1, pages + 1):
                for image in convert_from_path(
                    file_path, dpi=self.dpi, first_page=page_number, last_page=page_number
                ):
                    blocks.extend(self._blocks_from_image(image, page_number))
                    image.close()
        else:
            with Image.open(file_path) as image:
                blocks.extend(self._blocks_from_image(image, 1))
        return blocks

    @staticmethod
    def _blocks_from_image(image: Image.Image, page_number: int) -> list[dict]:
        data = pytesseract.image_to_data(image, output_type=Output.DICT)
        groups: "OrderedDict[int, dict]" = OrderedDict()

        for i in range(len(data["text"])):
            word = data["text"][i].strip()
            if not word:
                continue
            key = data["block_num"][i]
            x, y = data["left"][i], data["top"][i]
            w, h = data["width"][i], data["height"][i]
            g = groups.get(key)
            if g is None:
                groups[key] = {"words": [word], "x0": x, "y0": y, "x1": x + w, "y1": y + h}
            else:
                g["words"].append(word)
                g["x0"], g["y0"] = min(g["x0"], x), min(g["y0"], y)
                g["x1"], g["y1"] = max(g["x1"], x + w), max(g["y1"], y + h)

        return [
            {
                "page_number": page_number,
                "block_order": order,
                "text": " ".join(g["words"]),
                "bbox": [g["x0"], g["y0"], g["x1"] - g["x0"], g["y1"] - g["y0"]],
            }
            for order, g in enumerate(groups.values())
        ]
