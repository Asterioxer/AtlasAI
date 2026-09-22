import pytest

from app.services.ingestion import build_document
from app.services.embeddings import DeterministicEmbeddingProvider


@pytest.fixture
def embedding_provider() -> DeterministicEmbeddingProvider:
    return DeterministicEmbeddingProvider(dimensions=8)


def test_ingestion_pipeline_produces_indexable_chunks() -> None:
    document = build_document(
        "engineering.md",
        b"AtlasAI uses hybrid retrieval. Dense vectors capture semantic similarity."
    )
    assert document.chunks
    assert all(chunk.content for chunk in document.chunks)
