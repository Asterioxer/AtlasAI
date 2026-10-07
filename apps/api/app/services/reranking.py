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
    semantic_threshold: float = 0.42

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

            lexical_score = (coverage * 0.72) + phrase_bonus + min(exact_bonus, 0.24)
            semantic_score = max(0.0, min(hit.semantic_score, 1.0))

            if hit.semantic_score > 0.0:
                # Real semantic hits may not contain the literal query terms.
                # They are retained when the encoder reports meaningful
                # similarity, while lexical overlap still gets a bonus.
                if semantic_score < self.semantic_threshold and matched == 0:
                    continue
                score = (semantic_score * 0.72) + (coverage * 0.22) + phrase_bonus + min(exact_bonus, 0.24)
            else:
                # Deterministic vectors are not semantic evidence.
                if matched == 0:
                    continue
                score = lexical_score + min(max(hit.score, 0.0), 1.0) * 0.04

            scored.append((score, hit))

        scored.sort(key=lambda item: item[0], reverse=True)

        return [
            RetrievalHit(
                hit.chunk_id,
                round(score, 4),
                hit.source_id,
                hit.document_id,
                hit.content,
                hit.semantic_score,
            )
            for score, hit in scored[:top_k]
        ]
