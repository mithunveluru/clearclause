"""findings.impact + reports.pdf_path; reports.html_path nullable

Revision ID: 0008_impact_pdf
Revises: 0007_reports
Create Date: 2026-06-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_impact_pdf"
down_revision: Union[str, None] = "0007_reports"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("findings", sa.Column("impact", sa.Text(), nullable=True))
    op.add_column("reports", sa.Column("pdf_path", sa.String(length=512), nullable=True))
    op.alter_column("reports", "html_path", existing_type=sa.String(length=512), nullable=True)


def downgrade() -> None:
    op.alter_column("reports", "html_path", existing_type=sa.String(length=512), nullable=False)
    op.drop_column("reports", "pdf_path")
    op.drop_column("findings", "impact")