from fastapi import Depends, FastAPI

from app.api.deps import get_current_user
from app.api.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.models.user import User
from app.schemas.auth import UserOut

app = FastAPI(title="ClearClause API", version="0.1.0")

app.include_router(health_router)
app.include_router(auth_router)


@app.get("/api/v1/me", response_model=UserOut, tags=["auth"])
async def me(user: User = Depends(get_current_user)):
    return user


# Routers for documents/analysis are mounted in their phases.
