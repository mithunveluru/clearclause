from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.contracts import AnalyzerResult


@dataclass
class ClauseRef:
    id: int
    text: str
    page_number: int | None = None
    section_name: str | None = None


@dataclass
class AnalyzerContext:
    document_id: int
    classified_type: str
    document_family: str | None
    clauses: list[ClauseRef] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n".join(c.text for c in self.clauses)


class BaseAnalyzer(ABC):
    """One document family/type analyzer: extracts entities + findings and,
    for families that score themselves, a headline metric."""

    analyzer_type: str = "generic"
    document_family: str = "consumer"

    @abstractmethod
    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult: ...
