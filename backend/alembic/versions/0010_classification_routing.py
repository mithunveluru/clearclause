"""Add candidates_json and routing_action to document_classifications

Revision ID: 0010_classification_routing
Revises: 0009_v2_v3_core
Create Date: 2026-06-28

Additive and backward-compatible. Existing rows get routing_action='auto'
from server_default; candidates_json stays null until reprocessed.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_classification_routing"
down_revision: Union[str, None] = "0009_v2_v3_core"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "document_classifications",
        sa.Column("candidates_json", sa.JSON(), nullable=True),
    )
    op.add_column(
        "document_classifications",
        sa.Column(
            "routing_action",
            sa.String(length=10),
            nullable=False,
            server_default="auto",
        ),
    )


def downgrade() -> None:
    op.drop_column("document_classifications", "routing_action")
    op.drop_column("document_classifications", "candidates_json")
