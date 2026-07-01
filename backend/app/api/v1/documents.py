from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.ratelimit import rate_limit
from app.db.session import get_db
from app.models.user import User
from app.repositories.document_repo import DocumentRepository
from app.schemas.document import DocumentOut
from app.services.document_service import DocumentService
from app.worker.pipeline import dispatch

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


def _service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    return DocumentService(DocumentRepository(db))


@router.post(
    "/upload",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(limit=30, window=60, scope="upload"))],
)
async def upload(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    svc: DocumentService = Depends(_service),
):
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    content = await file.read(max_bytes + 1)  # bounded read: never load more than the cap
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB limit",
        )
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    doc = await svc.upload(user.id, file.filename or "upload", content)
    # Analysis starts automatically — no separate Analyze step.
    dispatch(doc.id, user.id)
    return doc


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    user: User = Depends(get_current_user),
    svc: DocumentService = Depends(_service),
):
    return await svc.list_documents(user.id)


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: int,
    user: User = Depends(get_current_user),
    svc: DocumentService = Depends(_service),
):
    return await svc.get(doc_id, user.id)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    user: User = Depends(get_current_user),
    svc: DocumentService = Depends(_service),
):
    await svc.delete(doc_id, user.id)
