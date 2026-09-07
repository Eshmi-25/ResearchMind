from app.ingestion.indexer import DocumentIndexer
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker
#TO RUN: python -m tests.test_reranker

indexer = DocumentIndexer()

documents = indexer.vector_store.documents

hybrid_retriever = HybridRetriever(
    documents=documents,
    vector_store=indexer.vector_store
)

reranker = Reranker()


query = "What is supervised learning?"


# First retrieve candidates
candidates = hybrid_retriever.search(
    query,
    top_k=5,
    alpha=0.5
)


print("\nHYBRID RESULTS")

for result in candidates:

    print(
        "\nChunk:",
        result["chunk_id"]
    )

    print(
        "Hybrid Score:",
        result["hybrid_score"]
    )

    print(
        result["text"][:200]
    )


# Then rerank them
reranked = reranker.rerank(
    query,
    candidates,
    top_k=3
)


print("\n\nRERANKED RESULTS")

for result in reranked:

    print(
        "\n-------------------------"
    )

    print(
        "Chunk:",
        result["chunk_id"]
    )

    print(
        "Rerank Score:",
        result["rerank_score"]
    )

    print(
        "Document:",
        result["document_name"]
    )

    print(
        "Text:",
        result["text"][:500]
    )