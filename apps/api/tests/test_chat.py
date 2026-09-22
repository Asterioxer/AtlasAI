import pytest

from app.services.chat import generate_grounded_answer
from app.services.llm import DeterministicLLMProvider
from app.services.retrieval import RetrievalHit


@pytest.mark.asyncio
async def test_grounded_answer_preserves_citations() -> None:
    hits = [RetrievalHit("c1", 0.8, "s1", "d1")]
    result = await generate_grounded_answer(
        "What is AtlasAI?",
        hits,
        DeterministicLLMProvider(),
    )
    assert result.response.model == "deterministic-local"
    assert result.citations == hits
