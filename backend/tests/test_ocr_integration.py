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
