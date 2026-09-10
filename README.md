![CI](https://github.com/medben13/opensearch/actions/workflows/ci.yml/badge.svg)

# OpenSearch

A portfolio-grade mini search engine demonstrating algorithms, information retrieval, databases, backend/frontend engineering, testing, containerization, and performance analysis.

## Features

- **Inverted index** for fast term lookup across the document collection
- **TF-IDF and BM25** ranking algorithms, selectable per query
- **PageRank** link-authority scoring, blended into final ranking alongside text relevance
- **REST API** built with FastAPI, including search, document lookup, and stats endpoints
- **React frontend** with a search box, algorithm selector, and result timing
- **Redis caching** for repeated searches
- **PostgreSQL** persistence with duplicate detection via content hashing
- **Web crawler** with `robots.txt` compliance, rate limiting, and domain restriction
- **Automated tests** (pytest) and **CI** (GitHub Actions) running on every push
- **Dockerized** — the full stack (backend, PostgreSQL, Redis) runs with one command

## Architecture

Browser
|
React Frontend
|
FastAPI REST API
|
+----------+--------------+
| | |
Search PostgreSQL Redis
Engine Database Cache
|
Inverted Index
^
|
Crawler


Search requests check Redis first; on a cache miss, the backend fetches documents from PostgreSQL, rebuilds the inverted index, ranks results with BM25/TF-IDF blended with PageRank, and caches the response for 5 minutes.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL (via SQLAlchemy) |
| Cache | Redis |
| Frontend | React (Vite) |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Deployment | Docker, Docker Compose |

## Installation

### Prerequisites
- Python 3.12+
- Node.js
- Docker Desktop

### Run everything with Docker (recommended)

```bash
git clone https://github.com/medben13/opensearch.git
cd opensearch
docker compose up
```

This starts the backend, PostgreSQL, and Redis together — no manual database or cache installation required. The API is available at `http://localhost:8000`.

### Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

### Manual backend setup (without Docker)

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1      # Windows
pip install -r requirements.txt
python create_tables.py
uvicorn app.main:app --reload
```

## API Examples

**Search:**

GET /api/v1/search?q=computer&algorithm=bm25

```json
{
  "query": "computer",
  "algorithm": "bm25",
  "total": 2,
  "results": [
    {
      "document_id": 42,
      "title": "Computer Science",
      "url": "https://example.com/1",
      "snippet": "Computer science is the study of...",
      "score": 14.82
    }
  ],
  "cached": false
}
```

**Other endpoints:**

GET /api/v1/documents/{id}
GET /api/v1/stats
POST /api/v1/crawl


## Search Algorithms

- **TF-IDF** scores terms by how frequently they appear in a document, weighted by how rare they are across the whole collection.
- **BM25** improves on TF-IDF with term-frequency saturation (repetition stops mattering past a point) and document-length normalization (`k1=1.2`, `b=0.75`).
- **PageRank** scores documents by link authority — pages linked-to by many other pages rank higher — computed iteratively (20 iterations, damping factor 0.85) and blended into the final score alongside BM25/TF-IDF relevance.

## Performance Benchmarks

Measured on a 10,844-document collection:

| Metric | Result |
|---|---|
| Indexing throughput | ~31,000–37,000 documents/second |
| Search latency (avg, in-process) | ~3 ms |
| Uncached search (full request, cold) | 833 ms |
| Cached search (warm) | 45.8 ms |
| **Cache speedup** | **18.2x** |

**Three real bugs found via benchmarking at scale:**

1. **BM25 document-length recomputation** — `bm25_search` re-tokenized every document's full text on every search just to compute length for normalization. Fixed by caching token lists at index-build time. (~88x improvement on raw search latency.)
2. **PageRank recomputed per request** — every uncached search re-ran the full 20-iteration PageRank algorithm across all documents, regardless of query. Fixed by caching PageRank scores in Redis (10-minute TTL), since link structure changes far less often than search queries arrive.
3. **Linear document lookup in response building** — building the final response scanned the entire document list for every matching result (`next(d for d in documents if d.id == doc_id)`), rather than using a precomputed dictionary. At 10,844 documents with thousands of matches for common queries, this alone accounted for ~2.9 seconds of a single request. Fixed by building a `dict[id, document]` once per request instead. This was the dominant remaining cost after the first two fixes.

Each fix followed the same pattern: measure the real request path end-to-end (not just the piece being optimized), find the actual bottleneck, fix it, and re-measure to confirm. The second and third bugs were specifically invisible in isolated function-level benchmarks and only appeared when timing the full live endpoint — a good reminder that benchmarking any one function in isolation can hide costs elsewhere in the real request path.

## Testing

```bash
cd backend
pytest
```

9 tests covering the tokenizer, inverted index, and BM25 ranking behavior.

## Deployment

```bash
docker compose up
```

Builds and runs the backend, PostgreSQL, and Redis as isolated containers on a shared network, with PostgreSQL data persisted via a named Docker volume.

## Future Improvements

- Cache the built inverted index itself (currently rebuilt from PostgreSQL on every uncached search — the last known unaddressed per-request cost)
- Scale further with real crawled content (current 10,844 documents are synthetic, from a small template pool)
- Rate limiting and request size limits on public-facing endpoints