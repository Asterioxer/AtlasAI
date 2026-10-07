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
    evidence_blocks = []
    for index, hit in enumerate(hits, start=1):
        evidence_blocks.append(
            f"[{index}]\n"
            f"source_id: {hit.source_id}\n"
            f"document_id: {hit.document_id}\n"
            f"relevance: {hit.score:.4f}\n"
            f"content:\n{hit.content[:7000]}"
        )

    context = "\n\n---\n\n".join(evidence_blocks)
    prompt = (
        f"Question:\n{question}\n\n"
        f"Retrieved evidence:\n{context or '(No relevant evidence found.)'}\n\n"
        "Answer the question directly using only the retrieved evidence. "
        "Do not repeat the question, retrieval metadata, source IDs, or evidence blocks. "
        "Do not invent facts. Use [1], [2], etc. only when a claim is supported by "
        "the corresponding evidence. If the evidence does not answer the question, "
        "say exactly that the knowledge base does not contain enough information."
    )
    response = await provider.generate(prompt)
    return GroundedAnswer(response=response, citations=hits)
