from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .chat_schemas import ChatRequest
from .services.llm import DeterministicLLMProvider
from .services.streaming import stream_text

router = APIRouter(prefix="/api/v1")
provider = DeterministicLLMProvider()


@router.post("/workspaces/{workspace_id}/chat/stream")
async def chat_stream(workspace_id: str, payload: ChatRequest):
    result = await provider.generate(payload.question)
    return StreamingResponse(stream_text(result.text), media_type="text/plain")
