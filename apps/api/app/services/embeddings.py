from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text."""
        raise NotImplementedError


class DeterministicEmbeddingProvider(EmbeddingProvider):
    """Small deterministic provider for tests and local plumbing only."""

    def __init__(self, dimensions: int = 8) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for i, char in enumerate(text.encode("utf-8")):
                vector[i % self.dimensions] += (char % 31) / 31.0
            norm = sum(value * value for value in vector) ** 0.5
            vectors.append([value / norm for value in vector] if norm else vector)
        return vectors
