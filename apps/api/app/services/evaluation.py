from dataclasses import dataclass

from .retrieval import RetrievalHit

@dataclass(frozen=True)
class EvaluationCase:
    query: str
    relevant_chunk_ids: set[str]

@dataclass(frozen=True)
class EvaluationResult:
    recall_at_k: float
    mrr: float

def evaluate_retrieval(cases: list[EvaluationCase], results: list[list[RetrievalHit]], k: int = 5) -> EvaluationResult:
    if not cases:
        return EvaluationResult(0.0, 0.0)
    recall_total = mrr_total = 0.0
    for case, hits in zip(cases, results):
        ids = [h.chunk_id for h in hits[:k]]
        recall_total += float(bool(case.relevant_chunk_ids.intersection(ids)))
        for rank, chunk_id in enumerate(ids, 1):
            if chunk_id in case.relevant_chunk_ids:
                mrr_total += 1.0 / rank
                break
    return EvaluationResult(recall_total / len(cases), mrr_total / len(cases))
