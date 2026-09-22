from app.services.chunking import chunk_text


def test_chunk_text_normalizes_and_preserves_overlap() -> None:
    chunks = chunk_text("alpha   beta gamma delta epsilon", chunk_size=18, overlap=5)
    assert chunks
    assert chunks[0].index == 0
    assert chunks[0].content
    assert all(chunk.index == i for i, chunk in enumerate(chunks))


def test_chunk_text_rejects_invalid_overlap() -> None:
    try:
        chunk_text("hello", chunk_size=10, overlap=10)
    except ValueError as exc:
        assert "smaller" in str(exc)
    else:
        raise AssertionError("expected ValueError")
