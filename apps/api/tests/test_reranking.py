from app.services.retrieval import RetrievalHit
from app.services.reranking import Reranker


def hit(chunk_id: str, content: str, score: float = 0.01) -> RetrievalHit:
    return RetrievalHit(chunk_id, score, "s1", "d1", content)


def test_exact_topic_beats_unrelated_chunk() -> None:
    ranked = Reranker().rerank(
        "Certifications",
        [
            hit("wrong", "Web Developer Intern built React components."),
            hit("right", "CERTIFICATIONS: OCI Generative AI and Data Science."),
        ],
    )
    assert ranked
    assert ranked[0].chunk_id == "right"
    assert ranked[0].score > 0.7


def test_unmatched_query_returns_no_evidence() -> None:
    ranked = Reranker().rerank(
        "red",
        [hit("wrong", "OCI Generative AI and Data Science.")],
    )
    assert ranked == []


def test_multi_term_query_requires_actual_overlap() -> None:
    ranked = Reranker().rerank(
        "OCI Generative AI",
        [
            hit("partial", "OCI Data Science certification."),
            hit("full", "OCI-certified in Generative AI and Data Science."),
        ],
    )
    assert ranked[0].chunk_id == "full"
