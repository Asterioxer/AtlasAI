import pytest

from app.services.ingestion import build_document
from app.services.parsing import UnsupportedDocumentType


def test_markdown_document_is_parsed_and_chunked() -> None:
    document = build_document("guide.md", b"# AtlasAI\n\nKnowledge retrieval works.")
    assert document.title == "guide.md"
    assert document.chunks


def test_pdf_adapter_is_explicitly_not_enabled() -> None:
    with pytest.raises(UnsupportedDocumentType):
        build_document("guide.pdf", b"%PDF")
