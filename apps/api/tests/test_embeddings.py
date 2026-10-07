import pytest

from app.services.embeddings import (
    DeterministicEmbeddingProvider,
    EmbeddingProviderError,
    HuggingFaceEmbeddingProvider,
)


@pytest.mark.asyncio
async def test_deterministic_provider_uses_configured_dimensions():
    provider = DeterministicEmbeddingProvider(dimensions=384)
    vectors = await provider.embed(["hello", "world"])
    assert len(vectors) == 2
    assert all(len(vector) == 384 for vector in vectors)
    assert provider.is_semantic is False


def test_huggingface_provider_parses_pooled_vectors():
    provider = HuggingFaceEmbeddingProvider.__new__(HuggingFaceEmbeddingProvider)
    provider.dimensions = 3

    vectors = provider._parse_batch([[1.0, 0.0, 0.0], [0.0, 3.0, 4.0]])
    assert len(vectors) == 2
    assert vectors[0] == pytest.approx([1.0, 0.0, 0.0])
    assert vectors[1] == pytest.approx([0.0, 0.6, 0.8])


def test_huggingface_provider_parses_token_embeddings():
    provider = HuggingFaceEmbeddingProvider.__new__(HuggingFaceEmbeddingProvider)
    provider.dimensions = 3

    vectors = provider._parse_batch([
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    ])
    assert vectors[0] == pytest.approx([2 ** -0.5, 2 ** -0.5, 0.0])


def test_huggingface_provider_rejects_wrong_dimensions():
    provider = HuggingFaceEmbeddingProvider.__new__(HuggingFaceEmbeddingProvider)
    provider.dimensions = 384

    with pytest.raises(EmbeddingProviderError):
        provider._parse_batch([[1.0, 2.0, 3.0]])
