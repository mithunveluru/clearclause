from fastapi import HTTPException, status

from app.core import files, storage
from app.models.document import Document
from app.repositories.document_repo import DocumentRepository
from app.repositories.report_repo import ReportRepository


class DocumentService:
    def __init__(self, repo: DocumentRepository, store: storage.Storage | None = None):
        self.repo = repo
        self.store = store or storage.get_storage()

    async def upload(self, user_id: int, filename: str, content: bytes) -> Document:
        try:
            ext = files.validate_extension(filename)
            source_type = files.detect_source_type(content)
            if source_type == "pdf":
                # Counting pages needs the bytes on disk. Inspect a throwaway copy, so
                # a rejected upload never reaches storage in the first place.
                with storage.temp_file(content, ext) as path:
                    files.validate_pdf_pages(path)
        except ValueError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

        key = storage.new_key("uploads", ext)
        self.store.put(key, content)
        return await self.repo.create(user_id, filename, key, source_type)

    async def list_documents(self, user_id: int) -> list[Document]:
        return await self.repo.list_for_user(user_id)

    async def get(self, doc_id: int, user_id: int) -> Document:
        doc = await self.repo.get_for_user(doc_id, user_id)
        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )
        return doc

    async def delete(self, doc_id: int, user_id: int) -> None:
        doc = await self.get(doc_id, user_id)
        # Remove the report object too (the DB row cascades, the object would orphan).
        report = await ReportRepository(self.repo.db).get(doc_id)
        if report and report.pdf_path:
            self.store.delete(report.pdf_path)
        self.store.delete(doc.file_path)
        await self.repo.delete(doc)
