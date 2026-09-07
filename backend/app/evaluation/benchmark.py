import time
"""
To measure the performance of the retrieval pipeline.
"""

def benchmark_retriever(
    retriever,
    queries: list[str],
    top_k: int = 5
) -> dict:

    if not queries:
        return {
            "queries": 0,
            "average_latency_ms": 0.0
        }

    latencies = []

    for query in queries:

        start = time.perf_counter()

        retriever.search(
            query,
            top_k=top_k
        )

        end = time.perf_counter()

        latency_ms = (
            end - start
        ) * 1000

        latencies.append(
            latency_ms
        )

    return {
        "queries": len(queries),
        "average_latency_ms": (
            sum(latencies)
            / len(latencies)
        ),
        "min_latency_ms": min(latencies),
        "max_latency_ms": max(latencies)
    }