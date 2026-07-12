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

    async def get_by_id(self, doc_id: int) -> Document | None:
        return await self.db.get(Document, doc_id)

    async def get_for_user(self, doc_id: int, user_id: int) -> Document | None:
        result = await self.db.execute(
            select(Document).where(
                Document.id == doc_id, Document.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def set_ocr_confidence(self, document_id: int, confidence: float | None) -> None:
        await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(ocr_confidence=confidence)
        )
        await self.db.commit()

    async def update_status(self, document_id: int, status: str) -> None:
        await self.db.execute(
            update(Document).where(Document.id == document_id).values(status=status)
        )
        await self.db.commit()

    async def set_qa_ready(self, document_id: int, ready: bool = True) -> None:
        await self.db.execute(
            update(Document).where(Document.id == document_id).values(qa_ready=ready)
        )
        await self.db.commit()

    async def set_ai_summary_ready(self, document_id: int, ready: bool = True) -> None:
        await self.db.execute(
            update(Document).where(Document.id == document_id).values(ai_summary_ready=ready)
        )
        await self.db.commit()

    async def start_reprocess(self, document_id: int) -> None:
        await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(
                status="uploaded",
                analysis_version=Document.analysis_version + 1,
                qa_ready=False,
                ai_summary_ready=False,
            )
        )
        await self.db.commit()

    async def set_classification(
        self, document_id: int, classified_type: str, document_family: str | None
    ) -> None:
        await self.db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(classified_type=classified_type, document_family=document_family)
        )
        await self.db.commit()

    async def delete(self, doc: Document) -> None:
        await self.db.delete(doc)
        await self.db.commit()
