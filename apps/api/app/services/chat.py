from dataclasses import dataclass

from .llm import LLMProvider, LLMResponse
from .retrieval import RetrievalHit


@dataclass(frozen=True)
class GroundedAnswer:
    response: LLMResponse
    citations: list[RetrievalHit]


async def generate_grounded_answer(
    question: str,
    hits: list[RetrievalHit],
    provider: LLMProvider,
) -> GroundedAnswer:
    context = "\n".join(
        f"[{index + 1}] chunk={hit.chunk_id} source={hit.source_id}"
        for index, hit in enumerate(hits)
    )
    prompt = f"Question: {question}\nContext:\n{context}"
    response = await provider.generate(prompt)
    return GroundedAnswer(response=response, citations=hits)
