import os
import uuid

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

# sniff magic bytes, not the extension — never trust the client at the upload boundary
_MAGIC = (
    (b"%PDF", "pdf"),
    (b"\x89PNG\r\n\x1a\n", "image"),
    (b"\xff\xd8\xff", "image"),  # JPEG
)


def validate_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext or 'unknown'}")
    return ext


def detect_source_type(content: bytes) -> str:
    for sig, kind in _MAGIC:
        if content.startswith(sig):
            return kind
    raise ValueError("File content does not match an allowed PDF/PNG/JPEG type")


def save_upload(content: bytes, ext: str) -> str:
    """Write bytes under a random name; never reuse the client filename in a path."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        f.write(content)
    return path


def new_report_path() -> str:
    os.makedirs(settings.REPORT_DIR, exist_ok=True)
    return os.path.join(settings.REPORT_DIR, f"{uuid.uuid4().hex}.pdf")


def delete_file(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
