"""Object storage for uploads and reports.

Files used to live on a container-local volume: unencrypted, unbacked, lost on
redeploy, and shared by path between the API and the worker — which is also what
stopped the worker from scaling past one host.

Keys look like "uploads/<uuid>.pdf". The S3 backend encrypts at rest and serves
reports through short-lived signed URLs, so bytes never pass through the API.
The local backend stays for development and tests.

OCR needs a real filesystem path (pdfplumber and pdf2image take paths, not bytes),
so `local_path()` hands out a temp copy that is cleaned up on exit. For the local
backend it just yields the file in place.
"""
import os
import tempfile
import uuid
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator

from app.core.config import settings


def new_key(prefix: str, ext: str) -> str:
    """A random key. The client filename never reaches a path."""
    return f"{prefix}/{uuid.uuid4().hex}{ext}"


class Storage(ABC):
    @abstractmethod
    def put(self, key: str, content: bytes) -> None: ...

    @abstractmethod
    def get(self, key: str) -> bytes: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    @contextmanager
    def local_path(self, key: str) -> Iterator[str]:
        """Yield a readable filesystem path for this object."""

    def signed_url(self, key: str, expires: int = 300) -> str | None:
        """A short-lived download URL, or None if the backend cannot issue one."""
        return None


class LocalStorage(Storage):
    def __init__(self, root: str | None = None):
        self.root = root or settings.STORAGE_DIR

    def _resolve(self, key: str) -> str:
        # Legacy rows hold an absolute path, not a key
        if os.path.isabs(key):
            return key
        path = os.path.normpath(os.path.join(self.root, key))
        if not path.startswith(os.path.abspath(self.root)):
            raise ValueError(f"key escapes the storage root: {key!r}")
        return path

    def put(self, key: str, content: bytes) -> None:
        path = self._resolve(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)

    def get(self, key: str) -> bytes:
        with open(self._resolve(key), "rb") as f:
            return f.read()

    def delete(self, key: str) -> None:
        try:
            os.remove(self._resolve(key))
        except FileNotFoundError:
            pass

    @contextmanager
    def local_path(self, key: str) -> Iterator[str]:
        yield self._resolve(key)  # already on disk; no copy needed


class S3Storage(Storage):
    def __init__(self):
        import boto3

        self.bucket = settings.S3_BUCKET
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL or None,  # set for R2/Spaces/MinIO
            region_name=settings.S3_REGION or None,
        )

    def put(self, key: str, content: bytes) -> None:
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ServerSideEncryption="AES256",  # encrypted at rest
        )

    def get(self, key: str) -> bytes:
        return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    @contextmanager
    def local_path(self, key: str) -> Iterator[str]:
        suffix = os.path.splitext(key)[1]
        fd, path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(self.get(key))
            yield path
        finally:
            os.unlink(path)  # the plaintext copy must not outlive the task

    def signed_url(self, key: str, expires: int = 300) -> str | None:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires,
        )


def get_storage() -> Storage:
    if settings.STORAGE_BACKEND == "s3":
        return S3Storage()
    if settings.STORAGE_BACKEND == "local":
        return LocalStorage()
    raise ValueError(f"Unknown STORAGE_BACKEND: {settings.STORAGE_BACKEND!r}")


@contextmanager
def temp_file(content: bytes, ext: str) -> Iterator[str]:
    """A throwaway local file — used to inspect an upload before it is stored."""
    fd, path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
        yield path
    finally:
        os.unlink(path)


def copy_into(path: str, key: str, storage: Storage) -> None:
    """Move a locally-produced file (a rendered PDF) into storage."""
    with open(path, "rb") as f:
        storage.put(key, f.read())
    os.unlink(path)


__all__ = [
    "LocalStorage",
    "S3Storage",
    "Storage",
    "copy_into",
    "get_storage",
    "new_key",
    "temp_file",
]
