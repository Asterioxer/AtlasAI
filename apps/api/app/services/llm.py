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
    """Local deterministic provider used for tests and zero-config development."""

    async def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            text=f"AtlasAI grounded response: {prompt[:500]}",
            model="deterministic-local",
        )


class HuggingFaceLLMProvider(LLMProvider):
    """OpenAI-compatible Hugging Face Inference Providers chat completion client."""

    def __init__(self, token: str, model: str, endpoint: str, timeout: float = 90.0):
        if not token:
            raise ValueError("HF_TOKEN is required for the Hugging Face provider")
        self.token = token
        self.model = model
        self.endpoint = endpoint
        self.timeout = timeout

    async def generate(self, prompt: str) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are AtlasAI, an enterprise knowledge assistant. "
                        "Answer ONLY from the supplied evidence. If evidence is insufficient, "
                        "say so explicitly. Never invent facts. Use [1], [2], etc. after claims "
                        "supported by evidence. Be concise but useful."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.15,
            "max_tokens": 900,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("LLM provider returned no choices")
        message = choices[0].get("message") or {}
        text = str(message.get("content") or "").strip()
        if not text:
            raise RuntimeError("LLM provider returned an empty response")
        return LLMResponse(text=text, model=str(data.get("model") or self.model))


class HTTPJSONLLMProvider(LLMProvider):
    """Legacy provider-neutral gateway: POST {prompt, model}, receive {text, model}."""

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


def build_llm_provider(
    provider: str,
    *,
    token: str = "",
    model: str = "Qwen/Qwen3-4B-Instruct-2507:cheapest",
    endpoint: str = "https://router.huggingface.co/v1/chat/completions",
    timeout: float = 90.0,
) -> LLMProvider:
    if provider.strip().lower() in {"huggingface", "hf", "inference-providers"}:
        return HuggingFaceLLMProvider(token, model, endpoint, timeout)
    return DeterministicLLMProvider()
