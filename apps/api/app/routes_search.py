from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth, require_workspace_access
from .db import get_db
from .models import Workspace
from .schemas import SearchRequest, SearchResponse, SearchResult
from .services.database_retrieval import lexical_search, vector_search
from .services.embeddings import DeterministicEmbeddingProvider
from .services.retrieval import reciprocal_rank_fusion
from .services.reranking import Reranker

router = APIRouter(prefix="/api/v1")
embedding_provider = DeterministicEmbeddingProvider()
reranker = Reranker()


@router.post("/workspaces/{workspace_id}/search", response_model=SearchResponse)
def search(
    workspace_id: UUID,
    payload: SearchRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
):
    require_workspace_access(workspace_id, auth, db)
    if db.get(Workspace, workspace_id) is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Workspace not found")
    lexical = lexical_search(db, str(workspace_id), payload.query, payload.limit)
    dense = vector_search(db, str(workspace_id), payload.query, embedding_provider, payload.limit)
    fused = reciprocal_rank_fusion(dense, lexical)
    ranked = reranker.rerank(payload.query, fused, payload.limit)
    return SearchResponse(results=[SearchResult(chunk_id=r.chunk_id, source_id=r.source_id, document_id=r.document_id, score=r.score) for r in ranked])
