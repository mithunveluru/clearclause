import pytest

from app.ocr import get_ocr_provider
from app.ocr.tesseract import TesseractOCRProvider


def test_factory_unknown_provider():
    with pytest.raises(ValueError):
        get_ocr_provider("does-not-exist")


def test_blocks_grouped_by_block_num(monkeypatch):
    # Fake Tesseract word data: two words in block 1, one in block 2, one blank.
    fake = {
        "block_num": [1, 1, 2, 2],
        "text": ["Processing", "fee", "", "Total"],
        "left": [10, 80, 0, 10],
        "top": [20, 20, 0, 60],
        "width": [60, 30, 0, 40],
        "height": [12, 12, 0, 12],
    }
    monkeypatch.setattr(
        "app.ocr.tesseract.pytesseract.image_to_data", lambda *a, **k: fake
    )

    blocks = TesseractOCRProvider._blocks_from_image(object(), page_number=3)

    assert [b["text"] for b in blocks] == ["Processing fee", "Total"]
    assert [b["block_order"] for b in blocks] == [0, 1]
    assert all(b["page_number"] == 3 for b in blocks)
    # block 1 bbox encloses both words: x0=10,y0=20,w=100,h=12
    assert blocks[0]["bbox"] == [10, 20, 100, 12]
