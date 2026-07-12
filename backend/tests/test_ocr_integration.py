"""Integration: real Tesseract OCR on a rendered image (skips without tesseract)."""
import os
import shutil
import tempfile

import pytest

pytestmark = pytest.mark.skipif(
    shutil.which("tesseract") is None, reason="tesseract binary not installed"
)


def test_real_ocr_extracts_text():
    from PIL import Image, ImageDraw

    from app.ocr import get_ocr_provider

    img = Image.new("RGB", (1000, 120), "white")
    d = ImageDraw.Draw(img)
    d.text((20, 30), "A processing fee of 2 percent applies.", fill="black")
    d.text((20, 70), "The plan will auto-renew monthly.", fill="black")
    path = os.path.join(tempfile.gettempdir(), "_ocr_integration.png")
    img.save(path)

    blocks = get_ocr_provider("tesseract").extract(path)
    os.remove(path)

    assert blocks, "OCR returned no blocks"
    text = " ".join(b["text"].lower() for b in blocks)
    assert "processing fee" in text
    assert all({"page_number", "block_order", "text", "bbox"} <= b.keys() for b in blocks)


def _page(rotate: int = 0):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (1240, 1754), "white")
    d = ImageDraw.Draw(img)
    y = 120
    for _ in range(10):
        d.text((90, y), "A processing fee of 2 percent applies on disbursal.", fill="black")
        y += 45
        d.text((90, y), "The plan will auto-renew monthly unless cancelled.", fill="black")
        y += 70
    return img.rotate(rotate, expand=True) if rotate else img


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_rotated_scans_are_read(rotation, tmp_path):
    """A page scanned sideways or upside down must still be read.

    Tesseract only reads horizontal text, so before this a 90-degree scan produced
    pure garbage and the document came back with no findings — which renders as
    "nothing risky here". This is the check the OSD-based attempt never had.
    """
    from app.ocr import get_ocr_provider

    path = str(tmp_path / f"scan-{rotation}.png")
    _page(rotation).save(path)

    blocks = get_ocr_provider("tesseract").extract(path)
    # The bundled bitmap font kerns tightly, so Tesseract runs some words together
    # ("willautorenew"). Strip spaces before matching: we are testing that the page
    # was turned the right way up, not how the test font renders.
    text = " ".join(b["text"].lower() for b in blocks)
    squashed = text.replace(" ", "").replace("-", "")

    assert "processingfee" in squashed, f"{rotation}deg page not recovered: {text[:100]!r}"
    assert "autorenew" in squashed
    assert blocks[0]["confidence"] > 60, "recovered text should read with confidence"
