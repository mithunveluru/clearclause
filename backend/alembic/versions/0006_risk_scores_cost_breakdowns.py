"""risk_scores and cost_breakdowns tables

Revision ID: 0006_scores
Revises: 0005_findings
Create Date: 2026-06-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_scores"
down_revision: Union[str, None] = "0005_findings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("fee_opacity_score", sa.Integer(), nullable=False),
        sa.Column("penalty_score", sa.Integer(), nullable=False),
        sa.Column("consent_score", sa.Integer(), nullable=False),
        sa.Column("renewal_score", sa.Integer(), nullable=False),
        sa.Column("cancellation_score", sa.Integer(), nullable=False),
    )
    op.create_index("ix_risk_scores_document_id", "risk_scores", ["document_id"])

    op.create_table(
        "cost_breakdowns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("headline_rate", sa.Float(), nullable=True),
        sa.Column("processing_fee", sa.Float(), nullable=True),
        sa.Column("late_fee", sa.Float(), nullable=True),
        sa.Column("renewal_fee", sa.Float(), nullable=True),
        sa.Column("foreclosure_charge", sa.Float(), nullable=True),
        sa.Column("estimated_true_cost", sa.Float(), nullable=True),
    )
    op.create_index("ix_cost_breakdowns_document_id", "cost_breakdowns", ["document_id"])


def downgrade() -> None:
    op.drop_index("ix_cost_breakdowns_document_id", table_name="cost_breakdowns")
    op.drop_table("cost_breakdowns")
    op.drop_index("ix_risk_scores_document_id", table_name="risk_scores")
    op.drop_table("risk_scores")
