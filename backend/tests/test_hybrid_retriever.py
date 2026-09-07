from app.ingestion.indexer import DocumentIndexer
from app.retrieval.hybrid_retriever import HybridRetriever


indexer = DocumentIndexer()

documents = indexer.vector_store.documents

retriever = HybridRetriever(
    documents=documents,
    vector_store=indexer.vector_store
)


results = retriever.search(
    "What is supervised learning?",
    top_k=5,
    alpha=0.5
)


print("\nHYBRID SEARCH RESULTS")

for result in results:

    print("\n-------------------------")

    print(
        "Hybrid Score:",
        result["hybrid_score"]
    )

    print(
        "Dense/Sparse Score:",
        result["score"]
    )

    print(
        "Document:",
        result["document_name"]
    )

    print(
        "Chunk ID:",
        result["chunk_id"]
    )

    print(
        "Text:",
        result["text"][:400]
    )