from app.ingestion.indexer import DocumentIndexer
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker
from app.generation.prompt import build_rag_prompt


indexer = DocumentIndexer()

documents = indexer.vector_store.documents

hybrid_retriever = HybridRetriever(
    documents=documents,
    vector_store=indexer.vector_store
)

reranker = Reranker()


query = "What is supervised learning?"


# Retrieve candidates
candidates = hybrid_retriever.search(
    query,
    top_k=5,
    alpha=0.5
)


# Rerank candidates
reranked = reranker.rerank(
    query,
    candidates,
    top_k=3
)


# Build prompt
prompt = build_rag_prompt(
    query,
    reranked
)


print("\n========== RAG PROMPT ==========\n")

print(prompt)