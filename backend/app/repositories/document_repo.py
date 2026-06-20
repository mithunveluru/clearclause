from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: int, original_filename: str, file_path: str, source_type: str
    ) -> Document:
        doc = Document(
            user_id=user_id,
            original_filename=original_filename,
            file_path=file_path,
            source_type=source_type,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def list_for_user(self, user_id: int) -> list[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(self, doc_id: int, user_id: int) -> Document | None:
        result = await self.db.execute(
            select(Document).where(
                Document.id == doc_id, Document.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def update_status(self, document_id: int, status: str) -> None:
        await self.db.execute(
            update(Document).where(Document.id == document_id).values(status=status)
        )
        await self.db.commit()

    async def delete(self, doc: Document) -> None:
        await self.db.delete(doc)
        await self.db.commit()
