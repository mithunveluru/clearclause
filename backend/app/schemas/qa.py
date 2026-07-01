from pydantic import BaseModel, Field


class QARequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
