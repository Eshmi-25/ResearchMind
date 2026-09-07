from rank_bm25 import BM25Okapi


class SparseRetriever:

    def __init__(
        self,
        documents: list[dict]
    ):

        self.documents = documents

        tokenized_documents = [
            document["text"].lower().split()
            for document in documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    def search(
        self,
        query: str,
        top_k: int = 5
    ):

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )[:top_k]

        results = []

        for index in ranked_indices:

            result = self.documents[index].copy()

            result["score"] = float(
                scores[index]
            )

            results.append(result)

        return results