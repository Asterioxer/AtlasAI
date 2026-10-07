from abc import ABC, abstractmethod
import math

import httpx


class EmbeddingProviderError(RuntimeError):
    """Raised when a semantic embedding provider cannot produce embeddings."""


class EmbeddingProvider(ABC):
    dimensions: int
    is_semantic: bool = False

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class DeterministicEmbeddingProvider(EmbeddingProvider):
    is_semantic = False

    def __init__(self, dimensions: int = 384) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for i, char in enumerate(text.encode("utf-8")):
                vector[i % self.dimensions] += (char % 31) / 31.0
            norm = math.sqrt(sum(value * value for value in vector))
            vectors.append([value / norm for value in vector] if norm else vector)
        return vectors


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """Hosted sentence embedding provider using HF Inference Providers."""

    is_semantic = True

    def __init__(
        self,
        token: str,
        model: str,
        dimensions: int = 384,
        endpoint: str = "",
        timeout: float = 60.0,
        batch_size: int = 16,
    ) -> None:
        if not token:
            raise EmbeddingProviderError("HF_TOKEN is required for semantic embeddings")
        if dimensions <= 0:
            raise ValueError("embedding dimensions must be positive")
        self.token = token
        self.model = model
        self.dimensions = dimensions
        self.endpoint = endpoint or (
            "https://router.huggingface.co/hf-inference/models/"
            f"{model}/pipeline/feature-extraction"
        )
        self.timeout = timeout
        self.batch_size = max(1, batch_size)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        vectors: list[list[float]] = []

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for start in range(0, len(texts), self.batch_size):
                batch = texts[start : start + self.batch_size]
                try:
                    response = await client.post(
                        self.endpoint,
                        headers=headers,
                        json={
                            "inputs": batch,
                            "normalize": True,
                            "truncate": True,
                            "truncation_direction": "right",
                        },
                    )
                    response.raise_for_status()
                    payload = response.json()
                except (httpx.HTTPError, ValueError) as exc:
                    detail = response.text[:500] if "response" in locals() else str(exc)
                    raise EmbeddingProviderError(
                        f"Hugging Face embedding request failed: {detail}"
                    ) from exc

                if not isinstance(payload, list) or len(payload) != len(batch):
                    raise EmbeddingProviderError(
                        "Hugging Face embedding response did not match the requested batch size"
                    )

                vectors.extend(self._parse_batch(payload))

        return vectors

    def _parse_batch(self, payload: list[object]) -> list[list[float]]:
        result: list[list[float]] = []
        for item in payload:
            # Most sentence-transformer deployments return one pooled vector.
            if self._is_vector(item):
                vector = [float(value) for value in item]  # type: ignore[arg-type]
            elif isinstance(item, list) and item and all(self._is_vector(row) for row in item):
                # Some feature-extraction deployments return token embeddings.
                rows = [[float(value) for value in row] for row in item]  # type: ignore[union-attr]
                width = len(rows[0])
                vector = [
                    sum(row[index] for row in rows) / len(rows)
                    for index in range(width)
                ]
            else:
                raise EmbeddingProviderError("Unsupported Hugging Face embedding response shape")

            if len(vector) != self.dimensions:
                raise EmbeddingProviderError(
                    f"Expected {self.dimensions}-D embeddings, received {len(vector)}-D"
                )

            norm = math.sqrt(sum(value * value for value in vector))
            result.append([value / norm for value in vector] if norm else vector)

        return result

    @staticmethod
    def _is_vector(value: object) -> bool:
        return isinstance(value, list) and bool(value) and all(
            isinstance(item, (int, float)) for item in value
        )


def build_embedding_provider(
    provider: str,
    *,
    token: str,
    model: str,
    dimensions: int,
    endpoint: str,
    timeout: float,
    batch_size: int,
) -> EmbeddingProvider:
    normalized = provider.strip().lower()
    if normalized in {"huggingface", "hf", "hf-inference"}:
        return HuggingFaceEmbeddingProvider(
            token=token,
            model=model,
            dimensions=dimensions,
            endpoint=endpoint,
            timeout=timeout,
            batch_size=batch_size,
        )
    if normalized in {"deterministic", "local"}:
        return DeterministicEmbeddingProvider(dimensions=dimensions)
    raise ValueError(f"Unsupported embedding provider: {provider}")
