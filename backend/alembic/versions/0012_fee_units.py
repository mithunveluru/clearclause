"""Record the unit each fee was written in.

Without it, cost_breakdowns.processing_fee = 4 could mean Rs 4 or 4% of the
principal, and every reader of that column — the PDF report, the AI summary, the
API — had to guess. Existing rows keep NULL: the unit was never captured for them,
and NULL says that honestly rather than inventing one.

Revision ID: 0012_fee_units
Revises: 0011_ocr_confidence
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012_fee_units"
down_revision: Union[str, None] = "0011_ocr_confidence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COLUMNS = (
    "processing_fee_unit",
    "late_fee_unit",
    "renewal_fee_unit",
    "foreclosure_charge_unit",
)


def upgrade() -> None:
    for column in _COLUMNS:
        op.add_column("cost_breakdowns", sa.Column(column, sa.String(length=8), nullable=True))


def downgrade() -> None:
    for column in reversed(_COLUMNS):
        op.drop_column("cost_breakdowns", column)
