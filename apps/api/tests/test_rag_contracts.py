from app.services.reranking import Reranker
from app.services.retrieval import RetrievalHit


def test_semantic_match_does_not_require_literal_query_terms():
    hit = RetrievalHit(
        chunk_id="semantic",
        score=0.0,
        source_id="s1",
        document_id="d1",
        content="Professional employment history and previous roles.",
        semantic_score=0.82,
    )
    ranked = Reranker().rerank("work experience", [hit], top_k=1)
    assert ranked[0].chunk_id == "semantic"


def test_zero_top_k_is_safe():
    assert Reranker().rerank("anything", [], top_k=0) == []
