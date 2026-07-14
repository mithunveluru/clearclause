"""The text-layer path: digital PDFs must not be rasterized and OCR'd."""
import pytest
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.ocr import get_ocr_provider
from app.ocr.base import OCRProvider
from app.ocr.pdftext import PdfTextProvider, _paragraphs


class SpyOCR(OCRProvider):
    """Stands in for Tesseract so we can see exactly which pages fell back."""

    def __init__(self):
        self.pages_ocred: list[int] = []

    def extract(self, file_path: str) -> list[dict]:
        raise AssertionError("whole-file OCR should not run for a PDF")

    def extract_page(self, file_path: str, page_number: int) -> list[dict]:
        self.pages_ocred.append(page_number)
        return [
            {"page_number": page_number, "block_order": 0, "text": "ocr fallback", "bbox": None}
        ]


def _digital_pdf(path, paragraphs_per_page: list[list[str]]) -> str:
    """A real PDF with a real text layer."""
    c = canvas.Canvas(str(path), pagesize=A4)
    for paragraphs in paragraphs_per_page:
        y = 780
        for para in paragraphs:
            for line in para.split("\n"):
                c.drawString(72, y, line)
                y -= 14          # normal line spacing
            y -= 22              # blank space between paragraphs
        c.showPage()
    c.save()
    return str(path)


def test_digital_pdf_uses_the_text_layer_and_never_ocrs(tmp_path):
    path = _digital_pdf(
        tmp_path / "loan.pdf",
        [[
            "A processing fee of 2 percent of the loan amount\nis payable upon disbursal.",
            "The borrower shall pay a penalty of 4 percent\non any prepayment made within 12 months.",
        ]],
    )
    spy = SpyOCR()
    blocks = PdfTextProvider(ocr=spy).extract(path)

    assert spy.pages_ocred == [], "a digital PDF was sent to OCR"
    text = " ".join(b["text"] for b in blocks)
    assert "processing fee of 2 percent" in text
    assert "penalty of 4 percent" in text


def test_sentences_are_not_split_across_line_breaks(tmp_path):
    # One block per line would split the clause
    path = _digital_pdf(
        tmp_path / "wrap.pdf",
        [["The subscription will automatically renew each month\nunless cancelled in writing."]],
    )
    blocks = PdfTextProvider(ocr=SpyOCR()).extract(path)

    joined = [b["text"] for b in blocks]
    assert any("automatically renew each month unless cancelled" in b for b in joined), joined


def test_paragraphs_are_kept_apart(tmp_path):
    path = _digital_pdf(
        tmp_path / "paras.pdf",
        [["First paragraph about fees.", "Second paragraph about renewal."]],
    )
    blocks = PdfTextProvider(ocr=SpyOCR()).extract(path)
    assert len(blocks) == 2, [b["text"] for b in blocks]


def test_page_without_a_text_layer_falls_back_to_ocr(tmp_path):
    # Page 1 has text; page 2 is a scan
    path = _digital_pdf(
        tmp_path / "mixed.pdf",
        [["A processing fee of 2 percent is payable upon disbursal of the loan."], []],
    )
    spy = SpyOCR()
    blocks = PdfTextProvider(ocr=spy).extract(path)

    assert spy.pages_ocred == [2], "the page without a text layer should have been OCR'd"
    assert any(b["text"] == "ocr fallback" and b["page_number"] == 2 for b in blocks)
    assert any("processing fee" in b["text"] for b in blocks)


def test_images_go_straight_to_ocr():
    class WholeFileSpy(SpyOCR):
        def extract(self, file_path: str) -> list[dict]:
            return [{"page_number": 1, "block_order": 0, "text": "image ocr", "bbox": None}]

    blocks = PdfTextProvider(ocr=WholeFileSpy()).extract("/tmp/scan.png")
    assert blocks[0]["text"] == "image ocr"


def test_paragraph_grouping_on_a_single_line():
    assert _paragraphs([]) == []
    one = [{"top": 0, "bottom": 10, "text": "x"}]
    assert _paragraphs(one) == [one]


def test_factory_selects_the_text_layer_provider_by_default():
    assert isinstance(get_ocr_provider("auto"), PdfTextProvider)
    with pytest.raises(ValueError):
        get_ocr_provider("does-not-exist")
