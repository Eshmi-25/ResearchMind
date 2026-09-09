from pathlib import Path

from app.database.vector_store import VectorStore
from app.retrieval.hybrid_retriever import HybridRetriever


VECTOR_STORE_PATH = (
    "data/processed/vector_store"
)


# --------------------------------------------------
# Shared vector store
# --------------------------------------------------

vector_store = VectorStore(
    dimension=384
)


# --------------------------------------------------
# Load existing vector store
# --------------------------------------------------

index_path = Path(
    VECTOR_STORE_PATH,
    "index.faiss"
)

documents_path = Path(
    VECTOR_STORE_PATH,
    "documents.pkl"
)


if (
    index_path.exists()
    and
    documents_path.exists()
):

    vector_store.load(
        VECTOR_STORE_PATH
    )


# --------------------------------------------------
# Shared retriever
# --------------------------------------------------

retriever = None


def rebuild_retriever():

    global retriever

    if vector_store.documents:

        retriever = HybridRetriever(
            documents=vector_store.documents,
            vector_store=vector_store
        )

    else:

        retriever = None