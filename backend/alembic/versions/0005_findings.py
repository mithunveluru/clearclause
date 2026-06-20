"""findings table

Revision ID: 0005_findings
Revises: 0004_clauses
Create Date: 2026-06-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_findings"
down_revision: Union[str, None] = "0004_clauses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "findings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "clause_id",
            sa.Integer(),
            sa.ForeignKey("clauses.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("issue_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("action_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_findings_document_id", "findings", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_findings_document_id", table_name="findings")
    op.drop_table("findings")
