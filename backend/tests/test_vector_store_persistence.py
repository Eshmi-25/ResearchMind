from app.database.vector_store import VectorStore


def test_vector_store_persistence(tmp_path):

    store = VectorStore(dimension=3)

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    documents = [
        {
            "text": "Machine learning"
        },
        {
            "text": "Computer networks"
        },
    ]

    store.add(
        embeddings,
        documents
    )

    store.save(
        str(tmp_path)
    )

    new_store = VectorStore(dimension=3)

    new_store.load(
        str(tmp_path)
    )

    results = new_store.search(
        [1.0, 0.0, 0.0],
        top_k=1
    )

    assert len(results) == 1

    assert results[0]["text"] == "Machine learning"

    assert "score" in results[0]