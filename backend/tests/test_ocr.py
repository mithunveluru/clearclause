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
    # Two words in block 1, one in block 2
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
    # Confidence is recorded, never used to remove text
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
    # Dropping garbled text would read as "no risks found"
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


# Function words tell real prose from confident OCR nonsense
_ENGLISH = "a processing fee of 2 percent is payable on the loan and is not refundable"
_NONSENSE = "pojjeoueassejun ayjuow mouarq;ne hmuedoul esingsipuosor iddeyusoiedzo"


def test_upright_page_is_not_rotated(monkeypatch):
    # The common case must cost exactly one OCR pass
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
    # Upside-down pages return high-confidence gibberish
    from PIL import Image

    def fake(image, **kwargs):
        upright = image.size == (100, 50)
        return _fake_read(_NONSENSE if upright else _ENGLISH, 88.0)

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", fake)

    blocks, angle = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 1)

    assert angle != 0, "confident gibberish was accepted as upright"
    assert "processing" in " ".join(b["text"] for b in blocks)


def test_bad_scan_keeps_the_page_as_found(monkeypatch):
    # Illegible at every angle is a poor scan
    from PIL import Image

    monkeypatch.setattr(
        "app.ocr.tesseract.pytesseract.image_to_data",
        lambda image, **kw: _fake_read(_NONSENSE, 30.0),
    )

    _, angle = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 1)

    assert angle == 0, "an unreadable page should not be rotated on a guess"


def test_a_rotation_must_be_readable_not_merely_better(monkeypatch):
    # A repayment schedule is mostly numbers: legitimately few function words.
    # Noise that scores 3 must not beat real text that scores 2.
    from PIL import Image

    def fake(image, **kwargs):
        upright = image.size == (100, 50)
        return _fake_read("of the 1200 4500 7800" if upright else "in a of 3300", 85.0)

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", fake)

    blocks, angle = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 1)

    assert angle == 0, "an illegible page was rotated on a 3-vs-2 function word guess"
    assert "1200" in " ".join(b["text"] for b in blocks)


def test_other_script_page_is_reread_in_the_fallback_language(monkeypatch):
    # Tamil pattas read as low-confidence Latin noise under the English model
    from PIL import Image

    def fake(image, config="", **kwargs):
        if "tam" in config:
            return _fake_read("patta land record chennai", 91.0)
        return _fake_read(_NONSENSE, 24.0)

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", fake)

    blocks, _ = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 1)

    assert "patta" in " ".join(b["text"] for b in blocks), "fallback alphabet was never tried"


def test_rotation_is_reused_across_pages(monkeypatch):
    # Pages share an orientation; only the first searches
    from PIL import Image

    passes = []

    def fake(image, **kwargs):
        passes.append(image.size)
        return _fake_read(_ENGLISH if image.size == (50, 100) else _NONSENSE, 90.0)

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", fake)

    _, angle = TesseractOCRProvider()._read_page(Image.new("RGB", (100, 50), "white"), 2, hint=90)

    assert angle == 90
    assert len(passes) == 1, "the hint should have been tried first and accepted"


def _capture_config(monkeypatch) -> list[str]:
    """Record the tesseract config string each read is issued with."""
    seen: list[str] = []

    def fake(image, config="", **kwargs):
        seen.append(config)
        return _fake_read("the loan of and to be", 90.0)

    monkeypatch.setattr("app.ocr.tesseract.pytesseract.image_to_data", fake)
    return seen


def test_no_resolution_is_claimed_for_an_image_that_declares_none(monkeypatch):
    # Asserting 300dpi on an upload nearer 100 tripled word error on the same file:
    # the claimed resolution is how Tesseract decides what point size it is reading.
    from PIL import Image

    seen = _capture_config(monkeypatch)
    TesseractOCRProvider()._read_page(Image.new("RGB", (600, 200), "white"), 1, dpi=None)

    assert seen, "no read was issued"
    assert all("--dpi" not in c for c in seen), f"a resolution was invented: {seen}"


def test_a_known_resolution_is_passed_through(monkeypatch):
    # Rasterized PDF pages: we chose the resolution, so Tesseract should be told
    from PIL import Image

    seen = _capture_config(monkeypatch)
    TesseractOCRProvider()._read_page(Image.new("RGB", (600, 200), "white"), 1, dpi=200)

    assert all("--dpi 200" in c for c in seen), f"the real resolution was withheld: {seen}"


def test_declared_dpi_is_read_from_the_file_only():
    from PIL import Image

    from app.ocr.tesseract import _declared_dpi

    assert _declared_dpi(Image.new("RGB", (10, 10))) is None
    with_dpi = Image.new("RGB", (10, 10))
    with_dpi.info["dpi"] = (150.0, 150.0)
    assert _declared_dpi(with_dpi) == 150
    # A zero is a malformed header, not a resolution
    zeroed = Image.new("RGB", (10, 10))
    zeroed.info["dpi"] = (0, 0)
    assert _declared_dpi(zeroed) is None
