from app.services.chunker import TextChunker


def test_chunker_splits_with_overlap() -> None:
    text = " ".join(f"token{i}" for i in range(120))
    chunker = TextChunker(chunk_size=120, chunk_overlap=20)

    chunks = chunker.split(text)

    assert len(chunks) > 1
    assert all(chunk.text for chunk in chunks)
    assert chunks[0].index == 0
    assert chunks[1].index == 1


def test_chunker_normalizes_blank_text() -> None:
    chunker = TextChunker()

    assert chunker.split(" \n\n\t ") == []
