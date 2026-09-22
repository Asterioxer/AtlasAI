from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth
from .db import get_db
from .services.database_retrieval import lexical_search

router = APIRouter(prefix="/api/v1")


@router.post("/workspaces/{workspace_id}/search")
async def search(
    workspace_id: UUID,
    payload: dict,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_auth),
):
    query = str(payload.get("query", "")).strip()
    limit = max(1, min(int(payload.get("limit", 8)), 50))
    if not query:
        return {"results": []}
    hits = lexical_search(db, str(workspace_id), query, limit)
    return {"results": [hit.__dict__ for hit in hits]}
