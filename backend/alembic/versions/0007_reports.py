"""reports table

Revision ID: 0007_reports
Revises: 0006_scores
Create Date: 2026-06-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_reports"
down_revision: Union[str, None] = "0006_scores"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("html_path", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reports_document_id", "reports", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_reports_document_id", table_name="reports")
    op.drop_table("reports")
