from datetime import datetime

from pydantic import BaseModel


class AISummaryOut(BaseModel):
    content: str
    model: str | None
    created_at: datetime
