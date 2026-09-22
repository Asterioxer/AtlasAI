from dataclasses import dataclass

from .chunking import TextChunk, chunk_text
from .parsing import parse_document


@dataclass(frozen=True)
class ParsedDocument:
    title: str
    content: str
    chunks: list[TextChunk]


def build_document(filename: str, content: bytes, chunk_size: int = 800, overlap: int = 120) -> ParsedDocument:
    text = parse_document(filename, content)
    return ParsedDocument(
        title=filename,
        content=text,
        chunks=chunk_text(text, chunk_size=chunk_size, overlap=overlap),
    )
