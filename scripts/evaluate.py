import json
from pathlib import Path

from app.database.vector_store import VectorStore
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import Reranker

from app.generation.prompt import build_rag_prompt
from app.generation.llm import generate_response

from app.evaluation.dataset import load_dataset
from app.evaluation.answer_metrics import (
    token_f1,
    exact_match
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

VECTOR_STORE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "vector_store"
)

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "evaluation_dataset.json"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "evaluation_results.json"
)


def main():

    print("Loading vector store...")

    vector_store = VectorStore(
        dimension=384
    )

    vector_store.load(
        VECTOR_STORE_PATH
    )

    documents = vector_store.documents

    print(
        f"Loaded {len(documents)} chunks."
    )

    print("Initializing retriever...")

    retriever = HybridRetriever(
        documents=documents,
        vector_store=vector_store
    )

    print("Loading reranker...")

    reranker = Reranker()

    print("Loading evaluation dataset...")

    dataset = load_dataset(
        DATASET_PATH
    )

    results = []

    total_f1 = 0.0
    total_exact_match = 0.0

    for index, sample in enumerate(
        dataset,
        start=1
    ):

        print(
            f"\nEvaluating {index}/{len(dataset)}:"
        )

        print(
            f"Question: {sample.question}"
        )

        # 1. Hybrid retrieval
        retrieved_documents = retriever.search(
            sample.question,
            top_k=5
        )

        # 2. Reranking
        reranked_documents = reranker.rerank(
            sample.question,
            retrieved_documents,
            top_k=3
        )

        # 3. Build RAG prompt
        prompt = build_rag_prompt(
            sample.question,
            reranked_documents
        )

        # 4. Generate answer
        generated_answer = generate_response(
            prompt
        )

        # 5. Calculate answer metrics
        f1 = token_f1(
            generated_answer,
            sample.answer
        )

        em = exact_match(
            generated_answer,
            sample.answer
        )

        total_f1 += f1
        total_exact_match += em

        result = {
            "question": sample.question,
            "reference_answer": sample.answer,
            "generated_answer": generated_answer,
            "token_f1": f1,
            "exact_match": em,
            "sources": [
                {
                    "document_name": document.get(
                        "document_name"
                    ),
                    "chunk_id": document.get(
                        "chunk_id"
                    )
                }
                for document in reranked_documents
            ]
        }

        results.append(result)

        print(
            f"Token F1: {f1:.4f}"
        )

        print(
            f"Exact Match: {em:.4f}"
        )

    # Calculate averages
    average_f1 = (
        total_f1 / len(dataset)
        if dataset
        else 0.0
    )

    average_exact_match = (
        total_exact_match / len(dataset)
        if dataset
        else 0.0
    )

    output = {
        "summary": {
            "questions": len(dataset),
            "average_token_f1": average_f1,
            "average_exact_match": (
                average_exact_match
            )
        },
        "results": results
    }

    # Save results
    results_path = Path(
        RESULTS_PATH
    )

    results_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        results_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n==============================")
    print("Evaluation Complete")
    print("==============================")

    print(
        f"Questions: {len(dataset)}"
    )

    print(
        f"Average Token F1: "
        f"{average_f1:.4f}"
    )

    print(
        f"Average Exact Match: "
        f"{average_exact_match:.4f}"
    )

    print(
        f"\nResults saved to:"
        f"\n{RESULTS_PATH}"
    )


if __name__ == "__main__":
    main()