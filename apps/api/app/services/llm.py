from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> LLMResponse:
        raise NotImplementedError


class DeterministicLLMProvider(LLMProvider):
    """Local deterministic provider used for tests and API plumbing."""

    async def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            text=f"AtlasAI grounded response: {prompt[:500]}",
            model="deterministic-local",
        )
