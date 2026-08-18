from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.core.storage import get_storage
from app.contracts import QAAnswer
from app.schemas.qa import QARequest
from app.services.qa_service import QAService
from app.db.session import get_db
from app.models.user import User
from app.repositories.ai_output_repo import AIOutputRepository
from app.repositories.analyzer_run_repo import AnalyzerRunRepository
from app.repositories.classification_repo import ClassificationRepository
from app.repositories.clause_repo import ClauseRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.score_repo import ScoreRepository
from app.schemas.ai import AISummaryOut
from app.schemas.classification import ClassificationOut, ClassificationOverrideIn, SecondaryCandidateOut
from app.schemas.entity import AnalysisOut, EntityOut
from app.schemas.explorer import ExplorerOut
from app.schemas.finding import FindingOut
from app.schemas.score import CostOut, ScoreBreakdown, ScoreOut
from app.scoring.risk import band, summarize
from app.services.document_service import DocumentService
from app.services.explorer_service import ExplorerService
from app.worker.pipeline import dispatch

router = APIRouter(prefix="/api/v1/documents", tags=["analysis"])


# Both routes below enqueue the full pipeline, so they cost what an upload costs.
# They are deliberately not charged against the monthly quota: reprocess is usually a
# retry of a failure that was ours, and billing the user for that is backwards.
@router.post(
    "/{doc_id}/analyze",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limit(limit=10, window=60, scope="analyze"))],
)
async def analyze(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enqueue analysis; returns immediately. Poll GET /documents/{id} for status."""
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    mode = dispatch(doc_id, user.id)
    return {"status": "queued", "pipeline": mode}


@router.post(
    "/{doc_id}/reprocess",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limit(limit=10, window=60, scope="reprocess"))],
)
async def reprocess(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-run the full pipeline; bumps analysis_version and resets AI flags."""
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    await DocumentRepository(db).start_reprocess(doc_id)
    mode = dispatch(doc_id, user.id)
    return {"status": "queued", "pipeline": mode}


@router.get("/{doc_id}/explorer", response_model=ExplorerOut)
async def get_explorer(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Interactive Document Explorer: structured sections, timeline, questions, walkthrough."""
    doc = await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    return await ExplorerService(
        FindingRepository(db),
        EntityRepository(db),
        ClauseRepository(db),
        ScoreRepository(db),
        AnalyzerRunRepository(db),
    ).build(doc_id, doc_type=doc.classified_type, document_family=doc.document_family)


@router.get("/{doc_id}/classification", response_model=ClassificationOut)
async def get_classification(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    row = await ClassificationRepository(db).get(doc_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not classified yet"
        )
    candidates = row.candidates_json or []
    return ClassificationOut(
        classified_type=row.classified_type,
        document_family=row.document_family,
        confidence=row.confidence,
        signals=row.signals_json or {},
        secondary_candidates=[
            SecondaryCandidateOut(**c) for c in candidates
        ],
        routing_action=row.routing_action or "auto",
        created_at=row.created_at,
    )


@router.patch("/{doc_id}/classification", response_model=ClassificationOut)
async def override_classification(
    doc_id: int,
    body: ClassificationOverrideIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """User override: correct the classifier's type selection."""
    from app.core.constants import FAMILY_OF, ClassifiedType
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    repo = ClassificationRepository(db)
    existing = await repo.get(doc_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not classified yet")
    valid_types = {v for k, v in ClassifiedType.__dict__.items() if not k.startswith("_")}
    if body.classified_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown document type '{body.classified_type}'. Valid: {sorted(valid_types)}",
        )
    doc_family = FAMILY_OF.get(body.classified_type)
    await repo.override(doc_id, body.classified_type, doc_family)
    await DocumentRepository(db).set_classification(doc_id, body.classified_type, doc_family)
    row = await repo.get(doc_id)
    return ClassificationOut(
        classified_type=row.classified_type,
        document_family=row.document_family,
        confidence=row.confidence,
        signals=row.signals_json or {},
        secondary_candidates=[],
        routing_action=row.routing_action or "auto",
        created_at=row.created_at,
    )


@router.get("/{doc_id}/entities", response_model=list[EntityOut])
async def list_entities(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    return await EntityRepository(db).list_for_document(doc_id)


@router.get("/{doc_id}/analysis", response_model=AnalysisOut)
async def get_analysis(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    run = await AnalyzerRunRepository(db).latest(doc_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analysis yet")
    return AnalysisOut(
        analyzer_type=run.analyzer_type,
        status=run.status,
        result=run.result_json,
        started_at=run.started_at,
        finished_at=run.finished_at,
    )


@router.post(
    "/{doc_id}/qa",
    response_model=QAAnswer,
    dependencies=[Depends(rate_limit(limit=20, window=60, scope="qa"))],
)
async def qa(
    doc_id: int,
    body: QARequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    if not doc.qa_ready:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Q&A is not available for this document (AI disabled or not indexed).",
        )
    return await QAService(db).answer(doc_id, body.question, doc_type=doc.classified_type)


@router.get("/{doc_id}/ai-summary", response_model=AISummaryOut)
async def get_ai_summary(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    out = await AIOutputRepository(db).latest(doc_id, "summary")
    if out is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No AI summary (AI may be disabled for this document)",
        )
    return AISummaryOut(content=out.content, model=out.model, created_at=out.created_at)


@router.get("/{doc_id}/findings", response_model=list[FindingOut])
async def list_findings(
    doc_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    rows = await FindingRepository(db).list_with_clause_text(doc_id)
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
            clause_text=clause_text,
        )
        for f, clause_text in rows
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
    """Serve the generated PDF report (opens in browser / downloadable)."""
    await DocumentService(DocumentRepository(db)).get(doc_id, user.id)
    report = await ReportRepository(db).get(doc_id)
    if report is None or not report.pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not generated yet"
        )

    store = get_storage()
    # Ownership checked above; the URL is short-lived
    url = store.signed_url(report.pdf_path)
    if url:
        return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    with store.local_path(report.pdf_path) as path:
        return FileResponse(
            path,
            media_type="application/pdf",
            filename=f"ClearClause-Report-{doc_id}.pdf",
            content_disposition_type="inline",
        )
