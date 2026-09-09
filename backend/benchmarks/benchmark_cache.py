import time
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/search"


def time_request(query: str, algorithm: str = "bm25") -> float:
    """
    Sends one real HTTP request to the search endpoint and returns
    the round-trip time in milliseconds.
    """
    start = time.perf_counter()
    response = requests.get(BASE_URL, params={"q": query, "algorithm": algorithm})
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms, response.json().get("cached", None)


def run_cache_benchmark():
    query = "computer science"

    print("--- Cache Benchmark ---")

    # First request: likely a cache MISS (unless something already searched
    # this exact query+algorithm combination recently, within the 5-minute TTL)
    cold_time, cold_cached = time_request(query)
    print(f"Request 1: {cold_time:.2f} ms (cached: {cold_cached})")

    # Second request, same query: should be a cache HIT
    warm_time, warm_cached = time_request(query)
    print(f"Request 2: {warm_time:.2f} ms (cached: {warm_cached})")

    if not cold_cached and warm_cached:
        speedup = cold_time / warm_time if warm_time > 0 else float("inf")
        print(f"\nCache speedup: {speedup:.1f}x faster")
    else:
        print("\nNote: results don't show a clean cold/warm pair -- "
              "try again, or check Redis is running.")


if __name__ == "__main__":
    run_cache_benchmark()