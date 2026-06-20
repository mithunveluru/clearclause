from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    original_filename: str
    source_type: str
    doc_type: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
