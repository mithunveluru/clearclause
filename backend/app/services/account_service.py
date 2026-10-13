"""Account-level operations: export everything, or erase everything.

Both exist because the DPDP Act gives a data principal the right to a copy of their
data and the right to have it deleted, and neither is something a user should have
to email support to obtain.
"""
import logging
from datetime import date, datetime
from typing import Any

from sqlalchemy import inspect

from app.core import storage
from app.models.user import User
from app.repositories.classification_repo import ClassificationRepository
from app.repositories.document_repo import DocumentRepository
from app.repositories.entity_repo import EntityRepository
from app.repositories.finding_repo import FindingRepository
from app.repositories.score_repo import ScoreRepository
from app.repositories.user_repo import UserRepository
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

# Never leaves the database, in an export or anywhere else
_SECRET_COLUMNS = {"password_hash"}


def _json_safe(value: Any) -> Any:
    return value.isoformat() if isinstance(value, (datetime, date)) else value


def _row(obj: Any) -> dict:
    """Every mapped column of one row, JSON-safe.

    Generic rather than a hand-written field list per model: a column added later is
    then exported by this code as it stands, instead of being quietly left out of
    everyone's export until someone notices.
    """
    return {
        column.key: _json_safe(getattr(obj, column.key))
        for column in inspect(obj).mapper.column_attrs
        if column.key not in _SECRET_COLUMNS
    }


class AccountService:
    def __init__(self, users: UserRepository, documents: DocumentRepository):
        self.users = users
        self.documents = documents
        self.db = users.db

    async def export(self, user: User) -> dict:
        """Everything held about this account, as one JSON document."""
        findings = FindingRepository(self.db)
        entities = EntityRepository(self.db)
        scores = ScoreRepository(self.db)
        classifications = ClassificationRepository(self.db)

        documents = []
        # No pagination: an export is meant to be complete, and retention caps the count
        for doc in await self.documents.list_for_user(user.id, limit=10_000, offset=0):
            risk = await scores.get_risk(doc.id)
            cost = await scores.get_cost(doc.id)
            classification = await classifications.get(doc.id)
            documents.append(
                {
                    **_row(doc),
                    "classification": _row(classification) if classification else None,
                    "risk_score": _row(risk) if risk else None,
                    "cost_breakdown": _row(cost) if cost else None,
                    "findings": [_row(f) for f in await findings.list_for_document(doc.id)],
                    "entities": [_row(e) for e in await entities.list_for_document(doc.id)],
                }
            )

        return {
            "exported_at": datetime.now().isoformat(),
            "account": _row(user),
            "documents": documents,
        }

    async def delete(self, user: User) -> None:
        """Erase the account and everything it owns.

        Rows cascade from the user, but the uploaded files, the generated reports and
        the vectors live outside Postgres — deleting the user alone would leave them
        behind, which is the opposite of what erasure means. So each document goes
        through the same path a single delete takes, and the user row goes last: a
        failure part-way leaves the account intact and retryable rather than a
        signed-out shell whose files are still in the bucket.
        """
        service = DocumentService(self.documents, storage.get_storage())
        for doc in await self.documents.list_for_user(user.id, limit=10_000, offset=0):
            await service.delete(doc.id, user.id)
        logger.info("erasing account %s", user.id)
        await self.users.delete(user)
