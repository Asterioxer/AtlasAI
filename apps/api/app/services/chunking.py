from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    content: str


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0
    step = chunk_size - overlap
    while start < len(normalized):
        content = normalized[start : start + chunk_size].strip()
        if content:
            chunks.append(TextChunk(index=index, content=content))
            index += 1
        start += step
    return chunks
