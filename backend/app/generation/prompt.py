def build_rag_prompt(
    query: str,
    documents: list[dict]
) -> str:

    context_parts = []

    for document in documents:

        context_parts.append(
            f"""
Source: {document["document_name"]}
Chunk: {document["chunk_id"]}

{document["text"]}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are ResearchMind, an AI research assistant.

Answer the user's question using ONLY the
provided context.

If the answer cannot be found in the context,
say that the information is not available
in the provided documents.

Do not invent facts.

User Question:
{query}

Context:
{context}

Instructions:
- Give a clear and concise answer.
- Use the provided context as your source of truth.
- Do not use outside knowledge.
- Mention the relevant source document.
- If multiple sources support the answer, mention them.
"""

    return prompt