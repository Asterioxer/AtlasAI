import pytest

from app.services.streaming import stream_text


@pytest.mark.asyncio
async def test_stream_text_yields_ordered_chunks() -> None:
    chunks = [chunk async for chunk in stream_text("abcdef", chunk_size=2)]
    assert chunks == ["ab", "cd", "ef"]
