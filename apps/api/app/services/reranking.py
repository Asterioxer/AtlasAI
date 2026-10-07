import re
from dataclasses import dataclass

from .retrieval import RetrievalHit


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was",
    "what", "when", "where", "which", "who", "with", "about", "tell", "me",
}


def _terms(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-zA-Z0-9]+(?:[+#][a-zA-Z0-9]+)*", text.lower())
        if token not in _STOPWORDS
    ]


@dataclass(frozen=True)
class Reranker:
    def rerank(self, query: str, hits: list[RetrievalHit], top_k: int = 5) -> list[RetrievalHit]:
        query_terms = list(dict.fromkeys(_terms(query)))
        if not query_terms:
            return []

        phrase = " ".join(query_terms)
        scored: list[tuple[float, RetrievalHit]] = []

        for hit in hits:
            content = hit.content.lower()
            content_terms = set(_terms(hit.content))
            matched = sum(1 for term in query_terms if term in content_terms)
            coverage = matched / len(query_terms)
            phrase_bonus = 0.35 if phrase and phrase in content else 0.0
            exact_bonus = 0.0
            for term in query_terms:
                if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", content):
                    exact_bonus += 0.08

            # Lexical evidence dominates the old deterministic vector score.
            # This prevents unrelated chunks from winning just because their
            # synthetic 8-D vectors happen to be close.
            score = (coverage * 0.72) + phrase_bonus + min(exact_bonus, 0.24) + min(max(hit.score, 0.0), 1.0) * 0.04
            if matched == 0:
                continue
            scored.append((score, hit))

        scored.sort(key=lambda item: item[0], reverse=True)

        results: list[RetrievalHit] = []
        for score, hit in scored[:top_k]:
            results.append(
                RetrievalHit(
                    hit.chunk_id,
                    round(score, 4),
                    hit.source_id,
                    hit.document_id,
                    hit.content,
                )
            )
        return results
