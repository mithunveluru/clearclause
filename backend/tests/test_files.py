import pytest
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.core.files import detect_source_type, validate_extension, validate_pdf_pages


def test_extension_allowlist():
    assert validate_extension("loan.PDF") == ".pdf"
    assert validate_extension("scan.jpeg") == ".jpeg"
    for bad in ("notes.txt", "macro.docx", "noext"):
        with pytest.raises(ValueError):
            validate_extension(bad)


def test_detect_source_type_by_magic_bytes():
    assert detect_source_type(b"%PDF-1.7\n...") == "pdf"
    assert detect_source_type(b"\x89PNG\r\n\x1a\n....") == "image"
    assert detect_source_type(b"\xff\xd8\xff\xe0JFIF") == "image"


def test_detect_source_type_rejects_disguised_content():
    # .pdf extension, plain-text content
    with pytest.raises(ValueError):
        detect_source_type(b"this is not really a pdf")


def _pdf_of(pages: int, path: str) -> str:
    c = canvas.Canvas(path)
    for i in range(pages):
        c.drawString(72, 720, f"page {i + 1}")
        c.showPage()
    c.save()
    return path


def test_pdf_page_cap(tmp_path):
    # The byte-size cap does not bound page count
    ok = _pdf_of(settings.MAX_PDF_PAGES, str(tmp_path / "ok.pdf"))
    assert validate_pdf_pages(ok) == settings.MAX_PDF_PAGES

    bomb = _pdf_of(settings.MAX_PDF_PAGES + 1, str(tmp_path / "bomb.pdf"))
    with pytest.raises(ValueError, match="limit"):
        validate_pdf_pages(bomb)


def test_corrupt_pdf_rejected_at_boundary(tmp_path):
    bad = tmp_path / "corrupt.pdf"
    bad.write_bytes(b"%PDF-1.7\nnot actually a pdf")
    with pytest.raises(ValueError):
        validate_pdf_pages(str(bad))
