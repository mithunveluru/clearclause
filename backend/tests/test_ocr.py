from types import SimpleNamespace

import pytest
from PIL import Image

from app.ocr import get_ocr_provider
from app.ocr import tesseract
from app.ocr.base import OCRProvider
from app.ocr.tesseract import TesseractOCRProvider
from app.services.ocr_service import OCRService


def test_factory_unknown_provider():
    with pytest.raises(ValueError):
        get_ocr_provider("does-not-exist")


def _no_rotation(monkeypatch):
    monkeypatch.setattr("app.ocr.tesseract._upright", lambda image: image)


def test_blocks_grouped_by_block_num(monkeypatch):
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
    _no_rotation(monkeypatch)
    monkeypatch.setattr(
        "app.ocr.tesseract.pytesseract.image_to_data", lambda *a, **k: fake
    )

    blocks = TesseractOCRProvider._blocks_from_image(object(), page_number=3)

    assert [b["text"] for b in blocks] == ["Processing fee", "Total"]
    assert [b["block_order"] for b in blocks] == [0, 1]
    assert all(b["page_number"] == 3 for b in blocks)
    # block 1 bbox encloses both words: x0=10,y0=20,w=100,h=12
    assert blocks[0]["bbox"] == [10, 20, 100, 12]


def test_page_mean_confidence_is_reported(monkeypatch):
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
    _no_rotation(monkeypatch)
    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", lambda *a, **k: fake)

    blocks = TesseractOCRProvider._blocks_from_image(object(), page_number=1)

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


def _osd(monkeypatch, rotate, conf):
    monkeypatch.setattr(
        "app.ocr.tesseract.pytesseract.image_to_osd",
        lambda *a, **k: {"rotate": rotate, "orientation_conf": conf},
    )


def test_confident_osd_rotates_the_page(monkeypatch):
    _osd(monkeypatch, rotate=90, conf=9.5)
    image = Image.new("RGB", (100, 50), "white")

    out = tesseract._upright(image)

    assert out.size == (50, 100), "a confidently sideways page was not rotated"


def test_unsure_osd_leaves_the_page_alone(monkeypatch):
    # OSD reports rotate=90 at 0.2 confidence — it is guessing. Acting on that would
    # turn a perfectly readable page into garbage, so we must not.
    _osd(monkeypatch, rotate=90, conf=0.2)
    image = Image.new("RGB", (100, 50), "white")

    assert tesseract._upright(image).size == (100, 50)


def test_osd_failure_leaves_the_page_alone(monkeypatch):
    def boom(*_a, **_kw):
        raise RuntimeError("Too few characters to estimate orientation")

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_osd", boom)
    image = Image.new("RGB", (100, 50), "white")

    assert tesseract._upright(image).size == (100, 50)
