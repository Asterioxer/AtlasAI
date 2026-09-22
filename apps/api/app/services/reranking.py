from dataclasses import dataclass

from .retrieval import RetrievalHit


@dataclass(frozen=True)
class Reranker:
    def rerank(self, query: str, hits: list[RetrievalHit], top_k: int = 5) -> list[RetrievalHit]:
        query_terms = {term.lower() for term in query.split() if term.strip()}
        scored = []
        for hit in hits:
            # Baseline keeps retrieval deterministic until a cross-encoder is configured.
            scored.append((hit.score, hit))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [hit for _, hit in scored[:top_k]]
