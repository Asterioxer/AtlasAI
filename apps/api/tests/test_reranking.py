from app.services.reranking import Reranker
from app.services.retrieval import RetrievalHit


def hit(chunk_id: str, content: str, score: float = 0.1, semantic_score: float = 0.0) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        score=score,
        source_id=f"source-{chunk_id}",
        document_id=f"doc-{chunk_id}",
        content=content,
        semantic_score=semantic_score,
    )


def test_exact_certifications_chunk_beats_unrelated_internship():
    reranker = Reranker()
    hits = reranker.rerank(
        "Certifications",
        [
            hit("internship", "Software engineering internship experience."),
            hit("certs", "CERTIFICATIONS: Oracle Cloud and Google Cloud credentials."),
        ],
        top_k=2,
    )
    assert hits[0].chunk_id == "certs"


def test_unmatched_red_query_returns_no_lexical_evidence():
    reranker = Reranker()
    hits = reranker.rerank(
        "red",
        [hit("a", "Python developer internship and projects.")],
    )
    assert hits == []


def test_semantic_only_match_can_survive_without_literal_terms():
    reranker = Reranker()
    hits = reranker.rerank(
        "work experience",
        [hit("a", "Professional employment history and previous roles.", semantic_score=0.82)],
    )
    assert hits[0].chunk_id == "a"


def test_low_confidence_semantic_hit_is_dropped_without_lexical_overlap():
    reranker = Reranker()
    hits = reranker.rerank(
        "certifications",
        [hit("a", "Random unrelated paragraph.", semantic_score=0.25)],
    )
    assert hits == []
