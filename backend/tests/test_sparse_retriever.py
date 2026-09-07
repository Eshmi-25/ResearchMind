from app.retrieval.sparse_retriever import SparseRetriever


documents = [
    {
        "text": "Machine learning is a branch of artificial intelligence."
    },
    {
        "text": "Supervised learning uses labelled training data."
    },
    {
        "text": "Random forests are ensemble learning algorithms."
    },
    {
        "text": "Neural networks are inspired by biological neurons."
    }
]


def test_sparse_retriever():

    retriever = SparseRetriever(documents)

    results = retriever.search(
        "supervised learning",
        top_k=2
    )

    assert len(results) == 2

    assert results[0]["text"] == (
        "Supervised learning uses labelled training data."
    )

    assert "score" in results[0]