# Models are added per phase (users, documents, jobs, ...). Importing this
# package registers every model on Base.metadata for Alembic autogenerate.
from app.models.user import User  # noqa: F401
from app.models.document import Document, Job  # noqa: F401
from app.models.extracted_block import ExtractedBlock  # noqa: F401
from app.models.clause import Clause  # noqa: F401
from app.models.finding import Finding  # noqa: F401
from app.models.score import CostBreakdown, RiskScore  # noqa: F401
from app.models.report import Report  # noqa: F401

