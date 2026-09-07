from app.retrieval.sparse_retriever import SparseRetriever


documents = [
    "Machine learning is a branch of artificial intelligence.",
    "Supervised learning uses labelled training data.",
    "Random forests are ensemble learning algorithms.",
    "Neural networks are inspired by biological neurons."
]


retriever = SparseRetriever(documents)


results = retriever.search(
    "supervised learning",
    top_k=2
)


for result in results:
    print("\nScore:", result["score"])
    print(result["document"])