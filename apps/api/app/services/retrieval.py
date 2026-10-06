from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    score: float
    source_id: str
    document_id: str
    content: str = ""


def reciprocal_rank_fusion(*ranked_lists: list[RetrievalHit], k: int = 60) -> list[RetrievalHit]:
    scores: dict[str, float] = {}
    representatives: dict[str, RetrievalHit] = {}
    for ranked in ranked_lists:
        for rank, hit in enumerate(ranked, start=1):
            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (k + rank)
            representatives.setdefault(hit.chunk_id, hit)

    return sorted(
        (
            RetrievalHit(
                representatives[chunk_id].chunk_id,
                score,
                representatives[chunk_id].source_id,
                representatives[chunk_id].document_id,
                representatives[chunk_id].content,
            )
            for chunk_id, score in scores.items()
        ),
        key=lambda hit: hit.score,
        reverse=True,
    )
