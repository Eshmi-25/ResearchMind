from fastapi import APIRouter

from app.schemas.query import (
    QueryRequest,
    QueryResponse
)

from app.database.vector_store import VectorStore
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker

from app.generation.prompt import build_rag_prompt
from app.generation.llm import generate_response
from app.generation.citation import extract_citations


router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


VECTOR_STORE_PATH = (
    "data/processed/vector_store"
)


# Load vector store once when the API starts
vector_store = VectorStore(
    dimension=384
)

vector_store.load(
    VECTOR_STORE_PATH
)


# Documents stored alongside FAISS
documents = vector_store.documents


retriever = HybridRetriever(
    documents=documents,
    vector_store=vector_store
)


reranker = Reranker()


@router.post(
    "",
    response_model=QueryResponse
)
def query(
    request: QueryRequest
):

    # 1. Hybrid retrieval
    retrieved_documents = retriever.search(
        request.query,
        top_k=request.top_k
    )

    # 2. Reranking
    reranked_documents = reranker.rerank(
        request.query,
        retrieved_documents,
        top_k=min(3, request.top_k)
    )

    # 3. Build RAG prompt
    prompt = build_rag_prompt(
        request.query,
        reranked_documents
    )

    # 4. Generate answer
    answer = generate_response(
        prompt
    )

    # 5. Extract citations
    sources = extract_citations(
        reranked_documents
    )

    return QueryResponse(
        answer=answer,
        sources=sources
    )