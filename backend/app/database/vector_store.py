import faiss
import numpy as np
import pickle

from pathlib import Path


class VectorStore:

    def __init__(
        self,
        dimension: int
    ):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.documents = []


    # --------------------------------------------------
    # Add documents
    # --------------------------------------------------

    def add(
        self,
        embeddings: list[list[float]],
        documents: list[dict]
    ):

        if not embeddings:
            return

        vectors = np.array(
            embeddings,
            dtype="float32"
        )

        faiss.normalize_L2(
            vectors
        )

        self.index.add(
            vectors
        )

        self.documents.extend(
            documents
        )


    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5
    ):

        if self.index.ntotal == 0:

            return []


        query_vector = np.array(
            [query_embedding],
            dtype="float32"
        )

        faiss.normalize_L2(
            query_vector
        )


        # Never ask FAISS for more vectors
        # than actually exist.

        actual_k = min(
            top_k,
            self.index.ntotal
        )


        scores, indices = self.index.search(
            query_vector,
            actual_k
        )


        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            result = self.documents[
                index
            ].copy()

            result["score"] = float(
                score
            )

            results.append(
                result
            )

        return results


    # --------------------------------------------------
    # Create filtered store
    # --------------------------------------------------

    def create_filtered_store(
        self,
        document_names: list[str]
    ):

        filtered_store = VectorStore(
            dimension=self.dimension
        )


        allowed_documents = set(
            document_names
        )


        selected_indices = [
            index
            for index, document
            in enumerate(self.documents)
            if document["document_name"]
            in allowed_documents
        ]


        if not selected_indices:

            return filtered_store


        # Reconstruct vectors from FAISS

        selected_vectors = np.array(
            [
                self.index.reconstruct(index)
                for index in selected_indices
            ],
            dtype="float32"
        )


        selected_documents = [
            self.documents[index].copy()
            for index in selected_indices
        ]


        # Add them to temporary store

        filtered_store.index.add(
            selected_vectors
        )

        filtered_store.documents = (
            selected_documents
        )


        return filtered_store


    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(
        self,
        directory: str
    ):

        path = Path(
            directory
        )

        path.mkdir(
            parents=True,
            exist_ok=True
        )


        faiss.write_index(
            self.index,
            str(
                path / "index.faiss"
            )
        )


        with open(
            path / "documents.pkl",
            "wb"
        ) as file:

            pickle.dump(
                self.documents,
                file
            )


    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    def load(
        self,
        directory: str
    ):

        path = Path(
            directory
        )


        index_path = (
            path / "index.faiss"
        )

        documents_path = (
            path / "documents.pkl"
        )


        if not index_path.exists():

            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )


        if not documents_path.exists():

            raise FileNotFoundError(
                f"Documents file not found: {documents_path}"
            )


        self.index = faiss.read_index(
            str(index_path)
        )


        with open(
            documents_path,
            "rb"
        ) as file:

            self.documents = pickle.load(
                file
            )