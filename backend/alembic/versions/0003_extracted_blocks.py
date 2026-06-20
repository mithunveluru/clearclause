"""extracted_blocks table

Revision ID: 0003_extracted_blocks
Revises: 0002_documents_jobs
Create Date: 2026-06-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_extracted_blocks"
down_revision: Union[str, None] = "0002_documents_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "extracted_blocks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("block_order", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("bbox_json", sa.JSON(), nullable=True),
    )
    op.create_index("ix_extracted_blocks_document_id", "extracted_blocks", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_extracted_blocks_document_id", table_name="extracted_blocks")
    op.drop_table("extracted_blocks")
