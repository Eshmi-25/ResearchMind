from app.embeddings.embedder import Embedder


def test_embedding():

    embedder = Embedder()

    vector = embedder.embed_text(
        "Machine learning is a branch of artificial intelligence."
    )

    assert len(vector) > 0
    assert all(isinstance(value, float) for value in vector)