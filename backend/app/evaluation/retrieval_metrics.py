"""
| Metric          | Meaning                                      |
| --------------- | -------------------------------------------- |
| Hit Rate        | Did we retrieve at least one relevant chunk? |
| Recall@K        | How many relevant chunks did we retrieve?    |
| Reciprocal Rank | How high was the first relevant result?      |
| MRR             | Average reciprocal rank across questions     |

"""

def _chunk_key(document: dict) -> tuple:
    return (
        document.get("document_name"),
        document.get("chunk_id")
    )


def hit_rate(
    retrieved_documents: list[dict],
    relevant_chunks: list[dict]
) -> float:

    if not relevant_chunks:
        return 0.0

    retrieved_keys = {
        _chunk_key(document)
        for document in retrieved_documents
    }

    relevant_keys = {
        _chunk_key(document)
        for document in relevant_chunks
    }

    return float(
        bool(retrieved_keys & relevant_keys)
    )


def recall_at_k(
    retrieved_documents: list[dict],
    relevant_chunks: list[dict]
) -> float:

    if not relevant_chunks:
        return 0.0

    retrieved_keys = {
        _chunk_key(document)
        for document in retrieved_documents
    }

    relevant_keys = {
        _chunk_key(document)
        for document in relevant_chunks
    }

    return len(
        retrieved_keys & relevant_keys
    ) / len(relevant_keys)


def reciprocal_rank(
    retrieved_documents: list[dict],
    relevant_chunks: list[dict]
) -> float:

    if not relevant_chunks:
        return 0.0

    relevant_keys = {
        _chunk_key(document)
        for document in relevant_chunks
    }

    for rank, document in enumerate(
        retrieved_documents,
        start=1
    ):

        if _chunk_key(document) in relevant_keys:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(
    results: list[float]
) -> float:

    if not results:
        return 0.0

    return sum(results) / len(results)