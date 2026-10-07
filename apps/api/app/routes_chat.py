from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth, require_workspace_access
from .chat_schemas import ChatRequest, ChatResponse
from .config import settings
from .conversation_models import Conversation, Message
from .db import get_db
from .models import Workspace
from .services.chat import generate_grounded_answer
from .services.database_retrieval import lexical_search, vector_search
from .services.embeddings import DeterministicEmbeddingProvider
from .services.llm import build_llm_provider
from .services.retrieval import reciprocal_rank_fusion
from .services.reranking import Reranker

router = APIRouter(prefix="/api/v1")
provider = build_llm_provider(
    settings.llm_provider,
    token=settings.hf_token,
    model=settings.llm_model,
    endpoint=settings.llm_endpoint,
    timeout=settings.llm_timeout_seconds,
)
embedding_provider = DeterministicEmbeddingProvider()
reranker = Reranker()


@router.post("/workspaces/{workspace_id}/chat", response_model=ChatResponse)
async def chat(
    workspace_id: UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
) -> ChatResponse:
    if db.get(Workspace, workspace_id) is None:
        raise HTTPException(404, "Workspace not found")
    require_workspace_access(workspace_id, auth, db)

    conversation = db.get(Conversation, payload.conversation_id) if payload.conversation_id else None
    if conversation is not None and conversation.workspace_id != workspace_id:
        raise HTTPException(400, "Conversation does not belong to workspace")
    if conversation is None:
        conversation = Conversation(workspace_id=workspace_id)
        db.add(conversation)
        db.flush()

    # Lexical retrieval is the source of truth until real semantic embeddings
    # are configured. The previous synthetic 8-D vectors were useful as a
    # placeholder but could rank unrelated chunks above exact matches.
    lexical = lexical_search(db, str(workspace_id), payload.question, limit=12)

    if lexical:
        dense = await vector_search(db, str(workspace_id), payload.question, embedding_provider, limit=12)
        lexical_ids = {hit.chunk_id for hit in lexical}
        dense_overlap = [hit for hit in dense if hit.chunk_id in lexical_ids]
        candidates = reciprocal_rank_fusion(lexical, dense_overlap)
    else:
        candidates = []

    hits = reranker.rerank(payload.question, candidates, 5)
    result = await generate_grounded_answer(payload.question, hits, provider)

    db.add(Message(conversation_id=conversation.id, role="user", content=payload.question))
    db.add(Message(conversation_id=conversation.id, role="assistant", content=result.response.text))
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        answer=result.response.text,
        model=result.response.model,
        citations=[
            {
                "chunk_id": hit.chunk_id,
                "source_id": hit.source_id,
                "document_id": hit.document_id,
                "score": hit.score,
            }
            for hit in result.citations
        ],
    )
