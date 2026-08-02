import logging
import statistics
from collections import OrderedDict

import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image
from pytesseract import Output

from app.core.config import settings
from app.ocr.base import OCRProvider

logger = logging.getLogger(__name__)

# Ordered by likelihood on a scanned page
_ANGLES = (0, 90, 270, 180)

# Upside-down text is confident nonsense; function words tell
_FUNCTION_WORDS = frozenset(
    "the of and to in a is for on or by with be as at from any all this that are not "
    "if may shall will per under within its it no".split()
)
_LEGIBLE_FUNCTION_WORDS = 4

# English only, add language detection if needed


class _Read:
    """One OCR pass at one rotation."""

    __slots__ = ("blocks", "words", "confidence", "function_words")

    def __init__(self, blocks: list[dict], words: int, confidence: float, function_words: int):
        self.blocks = blocks
        self.words = words
        self.confidence = confidence
        self.function_words = function_words

    @property
    def legible(self) -> bool:
        return self.function_words >= _LEGIBLE_FUNCTION_WORDS


class TesseractOCRProvider(OCRProvider):
    """CPU-only OCR via Tesseract, rasterizing PDFs page by page.

    Rotation is chosen by reading the page, not by Tesseract's OSD — OSD reported
    "rotate 180" at confidence 2.4 on upright pages and corrupted them.
    """

    def __init__(self, dpi: int = 200):
        self.dpi = dpi

    def extract_page(self, file_path: str, page_number: int, hint: int = 0) -> list[dict]:
        """OCR a single PDF page.

        One page at a time: converting all pages at once OOMs the worker (~26MB/page).
        """
        blocks: list[dict] = []
        for image in convert_from_path(
            file_path, dpi=self.dpi, first_page=page_number, last_page=page_number
        ):
            blocks.extend(self._read_page(image, page_number, hint)[0])
            image.close()
        return blocks

    def extract(self, file_path: str) -> list[dict]:
        blocks: list[dict] = []
        # Pages share an orientation; only the first searches
        hint = 0

        if file_path.lower().endswith(".pdf"):
            # Backstop; also enforced at upload
            pages = min(pdfinfo_from_path(file_path)["Pages"], settings.MAX_PDF_PAGES)
            for page_number in range(1, pages + 1):
                for image in convert_from_path(
                    file_path, dpi=self.dpi, first_page=page_number, last_page=page_number
                ):
                    page_blocks, hint = self._read_page(image, page_number, hint)
                    blocks.extend(page_blocks)
                    image.close()
        else:
            with Image.open(file_path) as image:
                blocks, _ = self._read_page(image, 1, hint)
        return blocks

    def _read_page(
        self, image: Image.Image, page_number: int, hint: int = 0
    ) -> tuple[list[dict], int]:
        """Blocks for this page, plus the rotation that produced them."""
        base = self._read(image, page_number, hint)
        if base.legible:
            return base.blocks, hint

        # A rotation must out-read the page as found
        best_angle, best = hint, base
        for angle in (a for a in _ANGLES if a != hint):
            read = self._read(image, page_number, angle)
            if read.function_words > best.function_words:
                best_angle, best = angle, read
            if read.legible:
                break

        if best_angle != hint:
            logger.info("page %d read %d degrees rotated", page_number, best_angle)
        if not best.blocks:
            # Bad scan, not an empty page
            logger.warning("page %d produced no usable text", page_number)
        return best.blocks, best_angle

    def _read(self, image: Image.Image, page_number: int, angle: int) -> _Read:
        rotated = image.rotate(angle, expand=True, fillcolor="white") if angle else image
        try:
            # Without the real dpi, confidences are meaningless
            data = pytesseract.image_to_data(
                rotated, output_type=Output.DICT, config=f"--dpi {self.dpi}"
            )
        finally:
            if rotated is not image:
                rotated.close()
        return self._blocks_from_data(data, page_number)

    @staticmethod
    def _blocks_from_data(data: dict, page_number: int) -> _Read:
        groups: "OrderedDict[int, dict]" = OrderedDict()
        confidences: list[float] = []

        for i in range(len(data["text"])):
            word = data["text"][i].strip()
            if not word:
                continue
            # Never filter by confidence: real words score 0
            confidences.append(float(data["conf"][i]))
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

        confidence = statistics.mean(confidences) if confidences else 0.0
        function_words = sum(
            1
            for g in groups.values()
            for w in g["words"]
            if w.strip(".,;:()").lower() in _FUNCTION_WORDS
        )
        blocks = [
            {
                "page_number": page_number,
                "block_order": order,
                "text": " ".join(g["words"]),
                "bbox": [g["x0"], g["y0"], g["x1"] - g["x0"], g["y1"] - g["y0"]],
                "confidence": confidence,  # page mean
            }
            for order, g in enumerate(groups.values())
        ]
        return _Read(blocks, len(confidences), confidence, function_words)
