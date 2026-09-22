from app.services.retrieval import RetrievalHit, reciprocal_rank_fusion


def test_rrf_merges_dense_and_lexical_rankings() -> None:
    dense = [RetrievalHit("a", 0.9, "s1", "d1"), RetrievalHit("b", 0.8, "s1", "d2")]
    lexical = [RetrievalHit("b", 0.7, "s1", "d2"), RetrievalHit("c", 0.6, "s2", "d3")]
    merged = reciprocal_rank_fusion(dense, lexical)
    assert {hit.chunk_id for hit in merged} == {"a", "b", "c"}
    assert merged[0].chunk_id == "b"
