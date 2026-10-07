from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth, require_workspace_access
from .config import settings
from .db import get_db
from .models import Workspace
from .schemas import SearchRequest, SearchResponse, SearchResult
from .services.database_retrieval import lexical_search, vector_search
from .services.embeddings import build_embedding_provider
from .services.retrieval import reciprocal_rank_fusion
from .services.reranking import Reranker

router = APIRouter(prefix="/api/v1")
embedding_provider = build_embedding_provider(
    settings.embedding_provider,
    token=settings.hf_token,
    model=settings.embedding_model,
    dimensions=settings.embedding_dimensions,
    endpoint=settings.embedding_endpoint,
    timeout=settings.embedding_timeout_seconds,
    batch_size=settings.embedding_batch_size,
)
reranker = Reranker()


@router.post("/workspaces/{workspace_id}/search", response_model=SearchResponse)
async def search(
    workspace_id: UUID,
    payload: SearchRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
) -> SearchResponse:
    if db.get(Workspace, workspace_id) is None:
        raise HTTPException(404, "Workspace not found")
    require_workspace_access(workspace_id, auth, db)

    lexical = lexical_search(db, str(workspace_id), payload.query, payload.limit)

    if embedding_provider.is_semantic:
        dense = await vector_search(
            db, str(workspace_id), payload.query, embedding_provider, payload.limit
        )
        candidates = reciprocal_rank_fusion(lexical, dense)
    else:
        candidates = lexical

    ranked = reranker.rerank(payload.query, candidates, payload.limit)
    return SearchResponse(
        results=[
            SearchResult(
                chunk_id=r.chunk_id,
                source_id=r.source_id,
                document_id=r.document_id,
                score=r.score,
            )
            for r in ranked
        ]
    )
