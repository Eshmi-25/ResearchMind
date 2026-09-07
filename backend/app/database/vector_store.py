import faiss
import numpy as np
import pickle
from pathlib import Path


class VectorStore:

    def __init__(self, dimension: int):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(dimension)

        self.documents = []

    def add(
        self,
        embeddings: list[list[float]],
        documents: list[dict]
    ):

        vectors = np.array(
            embeddings,
            dtype="float32"
        )

        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.documents.extend(documents)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5
    ):

        query_vector = np.array(
            [query_embedding],
            dtype="float32"
        )

        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(
            query_vector,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            result = self.documents[index].copy()

            result["score"] = float(score)

            results.append(result)

        return results

    def save(self, directory: str):

        path = Path(directory)

        path.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(path / "index.faiss")
        )

        with open(
            path / "documents.pkl",
            "wb"
        ) as file:

            pickle.dump(
                self.documents,
                file
            )

    def load(self, directory: str):

        path = Path(directory)

        index_path = path / "index.faiss"

        documents_path = path / "documents.pkl"

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

            self.documents = pickle.load(file)