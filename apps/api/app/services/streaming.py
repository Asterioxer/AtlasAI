from collections.abc import AsyncIterator


async def stream_text(text: str, chunk_size: int = 64) -> AsyncIterator[str]:
    for start in range(0, len(text), chunk_size):
        yield text[start : start + chunk_size]
