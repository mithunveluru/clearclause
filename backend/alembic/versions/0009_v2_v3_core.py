"""V2/V3 core: classifications, entities, analyzer_runs, chunks, ai_outputs + columns

Revision ID: 0009_v2_v3_core
Revises: 0008_impact_pdf
Create Date: 2026-06-21

Additive and backward-compatible — no backfill. Existing documents become
analysis_version=1 with null classification until reprocessed.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_v2_v3_core"
down_revision: Union[str, None] = "0008_impact_pdf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # documents columns
    op.add_column("documents", sa.Column("classified_type", sa.String(length=40), nullable=True))
    op.add_column("documents", sa.Column("document_family", sa.String(length=20), nullable=True))
    op.add_column("documents", sa.Column("analysis_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("documents", sa.Column("qa_ready", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("documents", sa.Column("ai_summary_ready", sa.Boolean(), nullable=False, server_default=sa.false()))

    # findings columns
    op.add_column("findings", sa.Column("document_family", sa.String(length=20), nullable=True))
    op.add_column("findings", sa.Column("analyzer_type", sa.String(length=40), nullable=True))

    # document_classifications
    op.create_table(
        "document_classifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("classified_type", sa.String(length=40), nullable=False),
        sa.Column("document_family", sa.String(length=20), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("signals_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_document_classifications_document_id", "document_classifications", ["document_id"])

    # document_entities
    op.create_table(
        "document_entities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(length=60), nullable=False),
        sa.Column("entity_value", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_document_entities_document_id", "document_entities", ["document_id"])

    # analyzer_runs
    op.create_table(
        "analyzer_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("analyzer_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_analyzer_runs_document_id", "analyzer_runs", ["document_id"])

    # document_chunks
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section_name", sa.String(length=255), nullable=True),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("vector_id", sa.String(length=64), nullable=True),
        sa.Column("embedding_provider", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])

    # ai_outputs
    op.create_table(
        "ai_outputs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("finding_id", sa.Integer(), sa.ForeignKey("findings.id", ondelete="CASCADE"), nullable=True),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=60), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_outputs_document_id", "ai_outputs", ["document_id"])
    op.create_index("ix_ai_outputs_input_hash", "ai_outputs", ["input_hash"])


def downgrade() -> None:
    op.drop_table("ai_outputs")
    op.drop_table("document_chunks")
    op.drop_table("analyzer_runs")
    op.drop_table("document_entities")
    op.drop_table("document_classifications")
    op.drop_column("findings", "analyzer_type")
    op.drop_column("findings", "document_family")
    op.drop_column("documents", "ai_summary_ready")
    op.drop_column("documents", "qa_ready")
    op.drop_column("documents", "analysis_version")
    op.drop_column("documents", "document_family")
    op.drop_column("documents", "classified_type")
