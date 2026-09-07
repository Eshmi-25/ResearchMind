from app.embeddings.embedder import Embedder
from app.retrieval.sparse_retriever import SparseRetriever


class HybridRetriever:

    def __init__(
        self,
        documents: list[dict],
        vector_store
    ):

        self.documents = documents
        self.vector_store = vector_store

        self.embedder = Embedder()

        self.sparse_retriever = SparseRetriever(
            documents
        )

    def _normalize_scores(
        self,
        results: list[dict]
    ):

        if not results:
            return results

        scores = [
            result["score"]
            for result in results
        ]

        min_score = min(scores)
        max_score = max(scores)

        if max_score == min_score:

            for result in results:
                result["normalized_score"] = 1.0

            return results

        for result in results:

            result["normalized_score"] = (
                (result["score"] - min_score)
                / (max_score - min_score)
            )

        return results

    def search(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.5
    ):

        # Dense retrieval
        query_embedding = self.embedder.embed_text(
            query
        )

        dense_results = self.vector_store.search(
            query_embedding,
            top_k=top_k
        )

        # Sparse retrieval
        sparse_results = self.sparse_retriever.search(
            query,
            top_k=top_k
        )

        # Normalize
        dense_results = self._normalize_scores(
            dense_results
        )

        sparse_results = self._normalize_scores(
            sparse_results
        )

        # Combine
        combined = {}

        for result in dense_results:

            key = (
                result["document_name"],
                result["chunk_id"]
            )

            combined[key] = {
                **result,
                "hybrid_score":
                    alpha
                    * result["normalized_score"]
            }

        for result in sparse_results:

            key = (
                result["document_name"],
                result["chunk_id"]
            )

            sparse_score = (
                (1 - alpha)
                * result["normalized_score"]
            )

            if key in combined:

                combined[key][
                    "hybrid_score"
                ] += sparse_score

            else:

                combined[key] = {
                    **result,
                    "hybrid_score":
                        sparse_score
                }

        # Rank
        ranked_results = sorted(
            combined.values(),
            key=lambda result:
                result["hybrid_score"],
            reverse=True
        )

        return ranked_results[:top_k]