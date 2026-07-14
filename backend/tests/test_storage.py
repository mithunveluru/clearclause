import os
from unittest.mock import MagicMock

import pytest

from app.core.storage import LocalStorage, S3Storage, new_key, temp_file


def test_local_roundtrip(tmp_path):
    store = LocalStorage(root=str(tmp_path))
    store.put("uploads/a.pdf", b"%PDF-1.7 hello")

    assert store.get("uploads/a.pdf") == b"%PDF-1.7 hello"
    with store.local_path("uploads/a.pdf") as path:
        assert open(path, "rb").read() == b"%PDF-1.7 hello"

    store.delete("uploads/a.pdf")
    assert not (tmp_path / "uploads" / "a.pdf").exists()
    store.delete("uploads/a.pdf")  # deleting twice is not an error


def test_local_rejects_keys_that_escape_the_root(tmp_path):
    store = LocalStorage(root=str(tmp_path))
    with pytest.raises(ValueError, match="escapes"):
        store.put("../../etc/passwd", b"x")


def test_local_honours_legacy_absolute_paths(tmp_path):
    # Legacy rows hold an absolute path, not a key
    legacy = tmp_path / "legacy.pdf"
    legacy.write_bytes(b"old")
    assert LocalStorage(root=str(tmp_path)).get(str(legacy)) == b"old"


def test_keys_are_random_and_never_reuse_the_client_filename():
    a, b = new_key("uploads", ".pdf"), new_key("uploads", ".pdf")
    assert a != b
    assert a.startswith("uploads/") and a.endswith(".pdf")


def test_temp_file_is_cleaned_up():
    with temp_file(b"secret", ".pdf") as path:
        assert open(path, "rb").read() == b"secret"
    assert not os.path.exists(path), "the plaintext copy outlived the context"


def _s3(monkeypatch) -> tuple[S3Storage, MagicMock]:
    client = MagicMock()
    boto3 = MagicMock()
    boto3.client.return_value = client
    monkeypatch.setitem(__import__("sys").modules, "boto3", boto3)
    monkeypatch.setattr("app.core.config.settings.S3_BUCKET", "cc-docs")
    return S3Storage(), client


def test_s3_encrypts_at_rest(monkeypatch):
    store, client = _s3(monkeypatch)
    store.put("uploads/a.pdf", b"contract")

    kwargs = client.put_object.call_args.kwargs
    assert kwargs["ServerSideEncryption"] == "AES256", "documents stored unencrypted"
    assert kwargs["Bucket"] == "cc-docs"
    assert kwargs["Key"] == "uploads/a.pdf"


def test_s3_signs_report_urls_with_a_short_expiry(monkeypatch):
    store, client = _s3(monkeypatch)
    client.generate_presigned_url.return_value = "https://cc-docs/x?sig=1"

    assert store.signed_url("reports/x.pdf") == "https://cc-docs/x?sig=1"
    assert client.generate_presigned_url.call_args.kwargs["ExpiresIn"] == 300


def test_local_backend_cannot_sign_urls(tmp_path):
    # None makes the endpoint stream the file instead
    assert LocalStorage(root=str(tmp_path)).signed_url("reports/x.pdf") is None


def test_s3_temp_copy_is_deleted_after_ocr(monkeypatch):
    store, client = _s3(monkeypatch)
    client.get_object.return_value = {"Body": MagicMock(read=lambda: b"%PDF bytes")}

    with store.local_path("uploads/a.pdf") as path:
        assert open(path, "rb").read() == b"%PDF bytes"
    assert not os.path.exists(path), "plaintext document left on the worker's disk"
