"""Does OCR come back with the *right* text?

Every other OCR test monkeypatches pytesseract, so they prove the plumbing around it
and nothing about the reading. These run the real engine over text this product
actually has to read — fees, rates, rupee amounts — and measure word error rate.

What this catches: a broken language or dpi config, rotation logic that mangles an
upright page, block assembly that drops or reorders words. Any of those turn every
document into "no risks found", which is the worst failure this product has because it
looks exactly like good news.

What this does NOT catch: real-scan degradation. Rendered text is clean — no skew, no
speckle, no photocopy ghosting. A real corpus in tests/fixtures/ocr_corpus, measured by
scripts/ocr_accuracy.py, is the only thing that speaks to accuracy in the field. This
is the floor, not the target.
"""
from pathlib import Path

import pytest
import reportlab
from PIL import Image, ImageDraw, ImageFont

from app.ocr.tesseract import TesseractOCRProvider
from scripts.ocr_accuracy import wer

# Ships inside reportlab, which is a hard dependency — so this cannot go missing the
# way a system font can when a base image changes
FONT_PATH = Path(reportlab.__file__).parent / "fonts" / "Vera.ttf"

# The wording that drives real findings: a percentage fee, a rupee fee, a rate, a term
CLAUSE_TEXT = (
    "A processing fee of 2 percent of the sanctioned amount shall be deducted "
    "before disbursal. Interest accrues at 14.5% per annum. A late payment "
    "charge of Rs. 500 applies to each missed instalment. Foreclosure before "
    "twenty four months attracts a charge of 4 percent of the outstanding "
    "principal. The lender may revise these charges with thirty days notice."
)

# Clean rendered text reads at 0.000 today. The allowance is headroom for font and
# engine differences across base images, not an accepted error rate.
MAX_WER = 0.05


def _render(text: str, words_per_line: int = 9) -> Image.Image:
    """Lay the text out as a page, at a size a real scan would produce."""
    words = text.split()
    lines = [
        " ".join(words[i : i + words_per_line]) for i in range(0, len(words), words_per_line)
    ]
    font = ImageFont.truetype(str(FONT_PATH), 30)
    image = Image.new("RGB", (1400, 60 + 46 * len(lines)), "white")
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(lines):
        draw.text((40, 30 + i * 46), line, fill="black", font=font)
    return image


def _read(image: Image.Image) -> str:
    blocks, _ = TesseractOCRProvider()._read_page(image, page_number=1)
    return " ".join(b["text"] for b in blocks)


def test_an_upright_page_is_read_accurately():
    assert wer(CLAUSE_TEXT, _read(_render(CLAUSE_TEXT))) <= MAX_WER


@pytest.mark.parametrize("figure", ["2", "14.5", "500", "4"])
def test_the_figures_that_drive_findings_survive(figure):
    # A misread digit is a wrong number shown to someone deciding whether to sign
    assert figure in _read(_render(CLAUSE_TEXT))


def test_an_upside_down_page_is_recovered():
    """The one orientation Tesseract cannot fix by itself.

    PSM 3 straightens a sideways page during layout analysis, so 90 and 270 read
    correctly with no help from us. A 180 flip needs OSD, which this provider
    deliberately does not use — it reported "rotate 180" at confidence 2.4 on upright
    pages and corrupted them. So the angle search exists for this case specifically.

    The angle it settles on is not the geometric inverse: from 180 it lands on 90 and
    lets Tesseract straighten the remaining quarter turn itself. What matters is that
    the text comes back, and that whatever angle it reports keeps working — that angle
    becomes the hint for every later page.
    """
    flipped = _render(CLAUSE_TEXT).rotate(180, expand=True, fillcolor="white")

    blocks, angle = TesseractOCRProvider()._read_page(flipped, page_number=1)
    text = " ".join(b["text"] for b in blocks)

    assert wer(CLAUSE_TEXT, text) <= MAX_WER, "an upside-down page was not recovered"

    # The reported angle must be reusable: it is applied verbatim to the next page
    reread = TesseractOCRProvider()._read_page(flipped, page_number=2, hint=angle)[0]
    assert wer(CLAUSE_TEXT, " ".join(b["text"] for b in reread)) <= MAX_WER, (
        "the angle reported for one page does not read the next one"
    )
