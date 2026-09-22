import pytest

from app.services.embeddings import DeterministicEmbeddingProvider


@pytest.mark.asyncio
async def test_deterministic_embeddings_are_normalized_and_stable() -> None:
    provider = DeterministicEmbeddingProvider(dimensions=8)
    first = await provider.embed(["atlas"])
    second = await provider.embed(["atlas"])
    assert first == second
    assert len(first[0]) == 8
    assert sum(value * value for value in first[0]) ** 0.5 == pytest.approx(1.0)
