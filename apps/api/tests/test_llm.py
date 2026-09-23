import pytest

from app.services.llm import DeterministicLLMProvider, HTTPJSONLLMProvider


@pytest.mark.asyncio
async def test_deterministic_provider_is_stable() -> None:
    result = await DeterministicLLMProvider().generate("hello")
    assert result.model == "deterministic-local"
    assert result.text.startswith("AtlasAI grounded response:")


def test_http_provider_configuration_is_provider_neutral() -> None:
    provider = HTTPJSONLLMProvider("http://localhost:9999/generate", "secret", "test-model")
    assert provider.endpoint.endswith("/generate")
    assert provider.model == "test-model"
