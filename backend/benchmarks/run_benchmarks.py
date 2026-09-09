import time
import statistics
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.services.document_service import get_all_documents
from app.search.index import InvertedIndex
from app.search.bm25 import bm25_search


def benchmark_indexing(documents):
    start = time.perf_counter()

    index = InvertedIndex()
    index.build_from_documents(documents)

    elapsed = time.perf_counter() - start
    throughput = len(documents) / elapsed if elapsed > 0 else float("inf")

    print(f"\n--- Indexing ---")
    print(f"Documents indexed: {len(documents)}")
    print(f"Time taken: {elapsed:.4f} seconds")
    print(f"Throughput: {throughput:.2f} documents/second")

    return index


def benchmark_search_latency(index, queries, runs=20):
    latencies = []

    for _ in range(runs):
        for query in queries:
            start = time.perf_counter()
            bm25_search(index, query)
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies.append(elapsed_ms)

    latencies.sort()
    avg = statistics.mean(latencies)
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95) - 1]

    print(f"\n--- Search Latency ({len(latencies)} searches) ---")
    print(f"Average: {avg:.3f} ms")
    print(f"P50 (median): {p50:.3f} ms")
    print(f"P95: {p95:.3f} ms")


def run_all_benchmarks():
    db = SessionLocal()
    documents = get_all_documents(db)
    db.close()

    if not documents:
        print("No documents found. Run load_sample_data.py first.")
        return

    index = benchmark_indexing(documents)

    sample_queries = ["computer", "data", "software engineering", "network security"]
    benchmark_search_latency(index, sample_queries)


if __name__ == "__main__":
    run_all_benchmarks()