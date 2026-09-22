from dataclasses import dataclass

from .retrieval import RetrievalHit


@dataclass(frozen=True)
class Reranker:
    """Deterministic baseline reranker; replace with cross-encoder provider later."""

    def rerank(self, query: str, hits: list[RetrievalHit], top_k: int = 5) -> list[RetrievalHit]:
        terms = {term.lower() for term in query.split() if term.strip()}
        scored = []
        for hit in hits:
            overlap = len(terms & set(hit.chunk_id.lower().split()))
            scored.append((hit.score + overlap * 0.001, hit))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [hit for _, hit in scored[:top_k]]
