def extract_citations(
    documents: list[dict]
) -> list[dict]:

    citations = []

    seen = set()

    for document in documents:

        key = (
            document.get("document_name"),
            document.get("chunk_id")
        )

        if key in seen:
            continue

        seen.add(key)

        citations.append({
            "document_name": document.get(
                "document_name"
            ),
            "chunk_id": document.get(
                "chunk_id"
            )
        })

    return citations