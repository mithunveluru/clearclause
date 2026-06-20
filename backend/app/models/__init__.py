# Models are added per phase (users, documents, jobs, ...). Importing this
# package registers every model on Base.metadata for Alembic autogenerate.
from app.models.user import User  # noqa: F401

