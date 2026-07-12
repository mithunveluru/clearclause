from types import SimpleNamespace

import pytest

from app.ocr import get_ocr_provider
from app.ocr.base import OCRProvider
from app.ocr.tesseract import TesseractOCRProvider
from app.services.ocr_service import OCRService


def test_factory_unknown_provider():
    with pytest.raises(ValueError):
        get_ocr_provider("does-not-exist")


def test_blocks_grouped_by_block_num():
    # Fake Tesseract word data: two words in block 1, one in block 2, one blank.
    fake = {
        "block_num": [1, 1, 2, 2],
        "text": ["Processing", "fee", "", "Total"],
        "conf": [96, 92, -1, 90],
        "left": [10, 80, 0, 10],
        "top": [20, 20, 0, 60],
        "width": [60, 30, 0, 40],
        "height": [12, 12, 0, 12],
    }
    blocks = TesseractOCRProvider._blocks_from_data(fake, page_number=3).blocks

    assert [b["text"] for b in blocks] == ["Processing fee", "Total"]
    assert [b["block_order"] for b in blocks] == [0, 1]
    assert all(b["page_number"] == 3 for b in blocks)
    # block 1 bbox encloses both words: x0=10,y0=20,w=100,h=12
    assert blocks[0]["bbox"] == [10, 20, 100, 12]


def test_page_mean_confidence_is_reported():
    # Confidence is recorded so a bad scan can be surfaced; it never removes text.
    fake = {
        "block_num": [1, 1, 1],
        "text": ["Processing", "fee", "|~,"],
        "conf": [90, 80, 10],
        "left": [10, 80, 130],
        "top": [20, 20, 20],
        "width": [60, 30, 8],
        "height": [12, 12, 12],
    }
    blocks = TesseractOCRProvider._blocks_from_data(fake, page_number=1).blocks

    assert blocks[0]["confidence"] == 60.0            # mean of 90, 80, 10
    assert "|~," in blocks[0]["text"], "text was dropped instead of scored"


class _StubBlocks:
    def __init__(self):
        self.saved = None

    async def replace_for_document(self, document_id, blocks):
        self.saved = blocks
        return len(blocks)


class _StubDocs:
    def __init__(self):
        self.confidence = "unset"

    async def set_ocr_confidence(self, document_id, confidence):
        self.confidence = confidence


class _StubProvider(OCRProvider):
    def __init__(self, blocks):
        self._blocks = blocks

    def extract(self, file_path):
        return self._blocks


async def test_low_confidence_is_recorded_not_discarded():
    # A garbled scan must still keep its text — dropping it would render the
    # document as "no risks found", which is the dangerous failure.
    blocks = [
        {"page_number": 1, "block_order": 0, "text": "penalty of 4 percent", "confidence": 22.0},
    ]
    docs, store = _StubDocs(), _StubBlocks()
    await OCRService(store, docs, provider=_StubProvider(blocks)).process(
        SimpleNamespace(id=1, file_path="/tmp/x.pdf")
    )

    assert docs.confidence == 22.0
    assert store.saved[0]["text"] == "penalty of 4 percent", "low-confidence text was dropped"


async def test_text_layer_documents_report_full_confidence():
    blocks = [{"page_number": 1, "block_order": 0, "text": "a clause", "confidence": 100.0}]
    docs = _StubDocs()
    await OCRService(_StubBlocks(), docs, provider=_StubProvider(blocks)).process(
        SimpleNamespace(id=1, file_path="/tmp/x.pdf")
    )
    assert docs.confidence == 100.0


def _fake_read(text: str, conf: float) -> dict:
    words = text.split()
    n = len(words)
    return {
        "block_num": [1] * n,
        "text": words,
        "conf": [conf] * n,
        "left": [10] * n,
        "top": [20] * n,
        "width": [30] * n,
        "height": [12] * n,
    }


# Real prose is full of function words; a page read at the wrong angle comes back as
# confident nonsense that contains none. That is what tells the two apart.
_ENGLISH = "a processing fee of 2 percent is payable on the loan and is not refundable"
_NONSENSE = "pojjeoueassejun ayjuow mouarq;ne hmuedoul esingsipuosor iddeyusoiedzo"


def test_upright_page_is_not_rotated(monkeypatch):
    # The common case must cost exactly one OCR pass. The old OSD-based code ran an
    # extra orientation pass on every page and still got it wrong.
    from PIL import Image

    calls = []

    def fake(image, **kwargs):
        calls.append(image.size)
        return _fake_read(_ENGLISH, 92.0)

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", fake)

    blocks, angle = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 1)

    assert angle == 0
    assert len(calls) == 1, "a legible page was OCR'd more than once"
    assert blocks


def test_confident_nonsense_does_not_pass_as_upright(monkeypatch):
    # The whole reason this is not decided on word count and confidence: an upside-down
    # page returns a *full page* of high-confidence gibberish. Only the rotation that
    # reads as English may win.
    from PIL import Image

    def fake(image, **kwargs):
        upright = image.size == (100, 50)
        return _fake_read(_NONSENSE if upright else _ENGLISH, 88.0)

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", fake)

    blocks, angle = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 1)

    assert angle != 0, "confident gibberish was accepted as upright"
    assert "processing" in " ".join(b["text"] for b in blocks)


def test_bad_scan_keeps_the_page_as_found(monkeypatch):
    # Nothing reads as English at any angle. That is a poor scan, not a rotated one —
    # the page must be left as it was rather than arbitrarily turned.
    from PIL import Image

    monkeypatch.setattr(
        "app.ocr.tesseract.pytesseract.image_to_data",
        lambda image, **kw: _fake_read(_NONSENSE, 30.0),
    )

    _, angle = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 1)

    assert angle == 0, "an unreadable page should not be rotated on a guess"


def test_rotation_is_reused_across_pages(monkeypatch):
    # Pages of one scan share an orientation, so only the first page pays to search.
    from PIL import Image

    passes = []

    def fake(image, **kwargs):
        passes.append(image.size)
        return _fake_read(_ENGLISH if image.size == (50, 100) else _NONSENSE, 90.0)

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", fake)

    _, angle = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 2, hint=90)

    assert angle == 90
    assert len(passes) == 1, "the hint should have been tried first and accepted"
