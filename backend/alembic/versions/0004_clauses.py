"""clauses table

Revision ID: 0004_clauses
Revises: 0003_extracted_blocks
Create Date: 2026-06-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_clauses"
down_revision: Union[str, None] = "0003_extracted_blocks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clauses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("clause_type", sa.String(length=30), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("section_name", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_clauses_document_id", "clauses", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_clauses_document_id", table_name="clauses")
    op.drop_table("clauses")
