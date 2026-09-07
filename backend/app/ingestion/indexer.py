from pathlib import Path

from app.ingestion.loader import load_pdf
from app.ingestion.cleaner import clean_text
from app.ingestion.chunker import chunk_text
from app.ingestion.metadata import create_chunk_metadata
from app.embeddings.embedder import Embedder
from app.database.vector_store import VectorStore


VECTOR_STORE_PATH = r"C:\Users\sumit\OneDrive\Desktop\ResearchMind\data\processed\vector_store"


class DocumentIndexer:

    def __init__(
        self,
        embedding_dimension: int = 384
    ):

        self.embedder = Embedder()

        self.vector_store = VectorStore(
            dimension=embedding_dimension
        )

        index_path = Path(
            VECTOR_STORE_PATH
        ) / "index.faiss"

        documents_path = Path(
            VECTOR_STORE_PATH
        ) / "documents.pkl"

        if index_path.exists() and documents_path.exists():

            self.vector_store.load(
                VECTOR_STORE_PATH
            )

    def index_document(self, file_path: str):

        raw_text = load_pdf(file_path)

        cleaned_text = clean_text(raw_text)

        chunks = chunk_text(cleaned_text)

        if not chunks:
            raise ValueError(
                "No text could be extracted from document."
            )

        embeddings = self.embedder.embed_documents(
            chunks
        )

        document_name = Path(file_path).name

        metadata = create_chunk_metadata(
            document_name,
            chunks
        )

        documents = []

        for chunk, meta in zip(chunks, metadata):

            documents.append({
                "text": chunk,
                "document_name": meta.document_name,
                "chunk_id": meta.chunk_id,
                "total_chunks": meta.total_chunks
            })

        self.vector_store.add(
            embeddings,
            documents
        )

        self.vector_store.save(
            VECTOR_STORE_PATH
        )

        return {
            "chunks": len(chunks),
            "embedding_dimension": len(embeddings[0])
        }

    def search(
        self,
        query: str,
        top_k: int = 5
    ):

        query_embedding = self.embedder.embed_text(
            query
        )

        return self.vector_store.search(
            query_embedding,
            top_k=top_k
        )