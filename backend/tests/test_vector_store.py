from app.database.vector_store import VectorStore


def test_vector_store():

    store = VectorStore(dimension=3)

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.9, 0.1, 0.0],
    ]

    documents = [
        "Machine learning",
        "Computer networks",
        "Supervised machine learning",
    ]

    store.add(embeddings, documents)

    results = store.search(
        [1.0, 0.0, 0.0],
        top_k=2
    )

    assert len(results) == 2
    assert results[0]["document"] == "Machine learning"