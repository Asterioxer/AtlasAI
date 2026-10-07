import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .auth import AuthContext, require_auth, require_workspace_access
from .chat_schemas import ChatRequest
from .config import settings
from .conversation_models import Conversation, Message
from .db import get_db
from .models import Workspace
from .services.chat import generate_grounded_answer
from .services.database_retrieval import lexical_search, vector_search
from .services.embeddings import build_embedding_provider
from .services.llm import build_llm_provider
from .services.retrieval import reciprocal_rank_fusion
from .services.reranking import Reranker
from .services.streaming import stream_text

router = APIRouter(prefix="/api/v1")

provider = build_llm_provider(
    settings.llm_provider,
    token=settings.hf_token,
    model=settings.llm_model,
    endpoint=settings.llm_endpoint,
    timeout=settings.llm_timeout_seconds,
)
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


@router.post("/workspaces/{workspace_id}/chat/stream")
async def chat_stream(
    workspace_id: UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_auth),
):
    if db.get(Workspace, workspace_id) is None:
        raise HTTPException(404, "Workspace not found")
    require_workspace_access(workspace_id, auth, db)

    conversation = (
        db.get(Conversation, payload.conversation_id)
        if payload.conversation_id
        else None
    )
    if conversation is not None and conversation.workspace_id != workspace_id:
        raise HTTPException(400, "Conversation does not belong to workspace")
    if conversation is None:
        normalized_title = " ".join(payload.question.split())[:117]
        if len(" ".join(payload.question.split())) > 120:
            normalized_title += "…"
        conversation = Conversation(
            workspace_id=workspace_id,
            title=normalized_title,
        )
        db.add(conversation)
        db.flush()
    elif not conversation.title:
        normalized_title = " ".join(payload.question.split())[:117]
        if len(" ".join(payload.question.split())) > 120:
            normalized_title += "…"
        conversation.title = normalized_title

    lexical = lexical_search(db, str(workspace_id), payload.question, limit=16)

    if embedding_provider.is_semantic:
        dense = await vector_search(
            db,
            str(workspace_id),
            payload.question,
            embedding_provider,
            limit=16,
        )
        candidates = reciprocal_rank_fusion(lexical, dense)
    else:
        candidates = lexical

    hits = reranker.rerank(payload.question, candidates, 5)
    result = await generate_grounded_answer(payload.question, hits, provider)

    db.add(Message(conversation_id=conversation.id, role="user", content=payload.question))
    db.add(Message(conversation_id=conversation.id, role="assistant", content=result.response.text))
    db.commit()

    citations = [
        {
            "chunk_id": c.chunk_id,
            "source_id": c.source_id,
            "document_id": c.document_id,
            "score": c.score,
        }
        for c in result.citations
    ]

    async def events():
        yield f"event: conversation\ndata: {json.dumps({'conversation_id': str(conversation.id)})}\n\n"
        async for chunk in stream_text(result.response.text):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield f"event: citations\ndata: {json.dumps({'citations': citations})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
