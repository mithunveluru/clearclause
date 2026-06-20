import pytest

from app.core.files import detect_source_type, validate_extension


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
    # .pdf extension but plain-text content must not pass the content sniff.
    with pytest.raises(ValueError):
        detect_source_type(b"this is not really a pdf")
