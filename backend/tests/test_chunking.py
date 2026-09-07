from app.ingestion.chunker import chunk_text


def test_chunk_text():
    text = "A" * 2500

    chunks = chunk_text(text)

    assert len(chunks) > 1
    assert all(len(chunk) > 0 for chunk in chunks)