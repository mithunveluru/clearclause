from fastapi import HTTPException, status

from app.core import files
from app.models.document import Document
from app.repositories.document_repo import DocumentRepository


class DocumentService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    async def upload(self, user_id: int, filename: str, content: bytes) -> Document:
        try:
            ext = files.validate_extension(filename)
            source_type = files.detect_source_type(content)
        except ValueError as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
        path = files.save_upload(content, ext)
        return await self.repo.create(user_id, filename, path, source_type)

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
        files.delete_file(doc.file_path)
        await self.repo.delete(doc)
