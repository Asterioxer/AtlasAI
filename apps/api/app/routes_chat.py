from fastapi import APIRouter

from .chat_schemas import ChatRequest, ChatResponse
from .services.chat import generate_grounded_answer
from .services.llm import DeterministicLLMProvider
from .services.retrieval import RetrievalHit

router = APIRouter(prefix="/api/v1")

provider = DeterministicLLMProvider()


@router.post("/workspaces/{workspace_id}/chat", response_model=ChatResponse)
async def chat(workspace_id: str, payload: ChatRequest) -> ChatResponse:
    # Retrieval becomes database-backed in the next Phase 3 increment.
    hits: list[RetrievalHit] = []
    result = await generate_grounded_answer(payload.question, hits, provider)
    return ChatResponse(
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
