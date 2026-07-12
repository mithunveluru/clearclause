"""Add ocr_confidence to documents

Revision ID: 0011_ocr_confidence
Revises: 0010_classification_routing
Create Date: 2026-07-12

Additive and backward-compatible. Nullable: existing rows stay null, which reads
as "unknown", and documents read from a PDF text layer have no OCR step to score.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_ocr_confidence"
down_revision: Union[str, None] = "0010_classification_routing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("ocr_confidence", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "ocr_confidence")
