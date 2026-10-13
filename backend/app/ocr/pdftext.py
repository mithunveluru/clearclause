"""Read a PDF's embedded text layer, OCR'ing only the pages that lack one.

Loan agreements and T&Cs are almost always digital PDFs that already carry their
text. Rasterizing those at 200dpi and running Tesseract over the pixels threw
that text away and re-derived it worse — every OCR error was self-inflicted, and
it cost seconds per page instead of milliseconds.

Scanned pages have no text layer, so those still go to Tesseract. The decision is
per page, not per document: a digital contract with a scanned signature page is
common, and each page takes the path that suits it.
"""
import statistics

import pdfplumber

from app.core.config import settings
from app.ocr.base import OCRProvider
from app.ocr.tesseract import TesseractOCRProvider

# Scanned pages still carry stray headers and watermarks
_MIN_CHARS_FOR_TEXT_LAYER = 40


def _paragraphs(lines: list[dict]) -> list[list[dict]]:
    """Group consecutive lines into paragraphs on vertical whitespace.

    The segmenter downstream splits blocks into sentences, so emitting one block
    per line would cut sentences at the line break and lose the clause. Paragraph
    blocks mirror what Tesseract's block grouping produces.

    A break is a vertical gap large relative to line height — not relative to the
    other gaps, since a lone gap can never look like an outlier among its peers.

    Gap heuristic; a layout-aware parser handles multi-column.
    """
    if len(lines) <= 1:
        return [lines] if lines else []

    line_height = statistics.median(ln["bottom"] - ln["top"] for ln in lines)
    limit = line_height * 0.75  # ordinary leading is a fraction of the glyph height

    groups: list[list[dict]] = [[lines[0]]]
    for previous, line in zip(lines, lines[1:]):
        if line["top"] - previous["bottom"] > limit:
            groups.append([line])
        else:
            groups[-1].append(line)
    return groups


def _blocks_from_page(page, page_number: int) -> list[dict]:
    lines = page.extract_text_lines()
    if sum(len(ln["text"].strip()) for ln in lines) < _MIN_CHARS_FOR_TEXT_LAYER:
        return []  # scanned page — caller falls back to OCR

    blocks = []
    for order, group in enumerate(_paragraphs(lines)):
        text = " ".join(ln["text"].strip() for ln in group).strip()
        if not text:
            continue
        x0 = min(ln["x0"] for ln in group)
        top = min(ln["top"] for ln in group)
        x1 = max(ln["x1"] for ln in group)
        bottom = max(ln["bottom"] for ln in group)
        blocks.append(
            {
                "page_number": page_number,
                "block_order": order,
                "text": text,
                # PDF points, not pixels; stored, never rendered
                "bbox": [x0, top, x1 - x0, bottom - top],
                # Read from the file, not OCR'd
                "confidence": 100.0,
            }
        )
    return blocks


class PdfTextProvider(OCRProvider):
    """Text layer first, Tesseract for pages (or files) without one."""

    def __init__(self, ocr: OCRProvider | None = None):
        self.ocr = ocr or TesseractOCRProvider()

    def extract(self, file_path: str) -> list[dict]:
        if not file_path.lower().endswith(".pdf"):
            return self.ocr.extract(file_path)  # images have no text layer

        blocks: list[dict] = []
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages[: settings.MAX_PDF_PAGES], start=1):
                page_blocks = _blocks_from_page(page, page_number)
                if not page_blocks:
                    page_blocks = self.ocr.extract_page(file_path, page_number)
                blocks.extend(page_blocks)
                page.close()  # pdfplumber caches per-page layout; drop it as we go
        return blocks
