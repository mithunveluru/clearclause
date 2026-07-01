from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    original_filename: str
    source_type: str
    doc_type: str | None
    classified_type: str | None
    document_family: str | None
    status: str
    qa_ready: bool
    ai_summary_ready: bool
    created_at: datetime

    model_config = {"from_attributes": True}
