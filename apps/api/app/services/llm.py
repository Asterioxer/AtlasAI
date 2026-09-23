from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx


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


class HTTPJSONLLMProvider(LLMProvider):
    """Provider-neutral HTTP gateway: POST {prompt, model}, receive {text, model}."""

    def __init__(self, endpoint: str, api_key: str | None = None, model: str = "atlasai-gateway"):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str) -> LLMResponse:
        headers = {"authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.endpoint,
                json={"prompt": prompt, "model": self.model},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return LLMResponse(text=str(data["text"]), model=str(data.get("model", self.model)))
