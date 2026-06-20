from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.clause_repo import ClauseRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.score_repo import ScoreRepository
from app.schemas.finding import FindingOut
from app.schemas.score import CostOut, ScoreBreakdown, ScoreOut
from app.scoring.risk import band, summarize
from app.services.document_service import DocumentService
from app.worker.tasks import run_analysis

router = APIRouter(prefix="/api/v1/documents", tags=["analysis"])


@router.post("/{doc_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enqueue analysis; returns immediately. Poll GET /documents/{id} for status."""
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    task = run_analysis.delay(doc_id, user.id)
    return {"status": "queued", "task_id": task.id}


@router.get("/{doc_id}/findings", response_model=list[FindingOut])
async def list_findings(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # ownership check (404 on others' docs)
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    clause_text = {
        c.id: c.normalized_text
        for c in await ClauseRepository(db).list_for_document(doc_id)
    }
    findings = await FindingRepository(db).list_for_document(doc_id)
    return [
        FindingOut(
            id=f.id,
            clause_id=f.clause_id,
            issue_type=f.issue_type,
            severity=f.severity,
            confidence=f.confidence,
            explanation=f.explanation,
            impact=f.impact,
            action_text=f.action_text,
            created_at=f.created_at,
            clause_text=clause_text.get(f.clause_id),
        )
        for f in findings
    ]


@router.get("/{doc_id}/score", response_model=ScoreOut)
async def get_score(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    scores = ScoreRepository(db)
    risk = await scores.get_risk(doc_id)
    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not scored yet"
        )
    cost = await scores.get_cost(doc_id)
    cats = {
        "total": risk.total_score,
        "fee_opacity": risk.fee_opacity_score,
        "penalty": risk.penalty_score,
        "renewal": risk.renewal_score,
        "consent": risk.consent_score,
        "cancellation": risk.cancellation_score,
    }
    return ScoreOut(
        total_score=risk.total_score,
        band=band(risk.total_score),
        summary=summarize(cats),
        breakdown=ScoreBreakdown(
            fee_opacity=risk.fee_opacity_score,
            penalty=risk.penalty_score,
            renewal=risk.renewal_score,
            consent=risk.consent_score,
            cancellation=risk.cancellation_score,
        ),
        cost=CostOut.model_validate(cost, from_attributes=True)
        if cost
        else CostOut(headline_rate=None, processing_fee=None, late_fee=None,
                     renewal_fee=None, foreclosure_charge=None, estimated_true_cost=None),
    )


@router.get("/{doc_id}/report")
async def get_report(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Serve the generated HTML report (opens in browser / downloadable)."""
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    report = await ReportRepository(db).get(doc_id)
    if report is None or not report.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not generated yet"
        )
    return FileResponse(
        report.pdf_path,
        media_type="application/pdf",
        filename=f"ClearClause-Report-{doc_id}.pdf",
        content_disposition_type="inline",
    )
