from fastapi import APIRouter, HTTPException

from app.schemas.query import (
    QueryRequest,
    QueryResponse
)

from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker

from app.generation.prompt import build_rag_prompt
from app.generation.llm import generate_response
from app.generation.citation import extract_citations

from app.core import state


router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


# --------------------------------------------------
# Reranker
# --------------------------------------------------

reranker = Reranker()


# --------------------------------------------------
# Query
# --------------------------------------------------

@router.post(
    "",
    response_model=QueryResponse
)
def query(
    request: QueryRequest
):

    # --------------------------------------------------
    # Check documents
    # --------------------------------------------------

    if not state.vector_store.documents:

        raise HTTPException(
            status_code=400,
            detail="No documents have been uploaded."
        )


    # --------------------------------------------------
    # Determine documents to search
    # --------------------------------------------------

    if request.selected_documents:

        selected_documents = [
            document
            for document in state.vector_store.documents
            if document["document_name"]
            in request.selected_documents
        ]

        if not selected_documents:

            raise HTTPException(
                status_code=400,
                detail="None of the selected documents were found."
            )

        # --------------------------------------------------
        # Create a temporary vector store containing
        # ONLY selected documents
        # --------------------------------------------------

        selected_store = state.vector_store.create_filtered_store(
            request.selected_documents
        )

        if not selected_store.documents:

            raise HTTPException(
                status_code=400,
                detail="No chunks found for selected documents."
            )

        filtered_retriever = HybridRetriever(
            documents=selected_store.documents,
            vector_store=selected_store
        )

        retrieved_documents = filtered_retriever.search(
            request.query,
            top_k=request.top_k
        )

    else:

        # --------------------------------------------------
        # Search all documents
        # --------------------------------------------------

        if state.retriever is None:

            state.rebuild_retriever()

        if state.retriever is None:

            raise HTTPException(
                status_code=400,
                detail="Retriever is not available."
            )

        retrieved_documents = state.retriever.search(
            request.query,
            top_k=request.top_k
        )


    # --------------------------------------------------
    # Reranking
    # --------------------------------------------------

    reranked_documents = reranker.rerank(
        request.query,
        retrieved_documents,
        top_k=min(
            3,
            request.top_k
        )
    )


    # --------------------------------------------------
    # Build RAG prompt
    # --------------------------------------------------

    prompt = build_rag_prompt(
        request.query,
        reranked_documents
    )


    # --------------------------------------------------
    # Generate answer
    # --------------------------------------------------

    answer = generate_response(
        prompt
    )


    # --------------------------------------------------
    # Extract citations
    # --------------------------------------------------

    sources = extract_citations(
        reranked_documents
    )


    # --------------------------------------------------
    # Return response
    # --------------------------------------------------

    return QueryResponse(
        answer=answer,
        sources=sources
    )