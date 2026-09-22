from app.services.reranking import Reranker
from app.services.retrieval import RetrievalHit


def test_reranker_respects_top_k() -> None:
    hits = [
        RetrievalHit("atlas", 0.8, "s1", "d1"),
        RetrievalHit("other", 0.7, "s1", "d2"),
    ]
    assert len(Reranker().rerank("atlas", hits, top_k=1)) == 1
