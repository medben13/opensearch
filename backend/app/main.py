import json
import time
import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import SessionLocal
from app.services.document_service import get_all_documents
from app.search.index import InvertedIndex
from app.search.tfidf import tfidf_search
from app.search.bm25 import bm25_search

app = FastAPI(title="OpenSearch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# One shared Redis connection, reused across every request rather than
# reconnecting each time -- connecting has overhead, so we do it once at startup.
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


@app.get("/api/v1/search")
def search(q: str, algorithm: str = "bm25"):
    # Build a cache key that uniquely represents THIS exact request.
    # Two different queries, or the same query with a different algorithm,
    # must produce different keys -- otherwise we'd return the wrong cached result.
    cache_key = f"search:{algorithm}:{q}"

    cached_result = redis_client.get(cache_key)
    if cached_result is not None:
        # Redis only stores strings -- json.loads converts the stored string
        # back into a real Python dict/list.
        result = json.loads(cached_result)
        result["cached"] = True
        return result

    db = SessionLocal()
    documents = get_all_documents(db)

    index = InvertedIndex()
    index.build_from_documents(documents)

    if algorithm == "tfidf":
        results = tfidf_search(index, q)
    else:
        results = bm25_search(index, q)

    response_results = []
    for doc_id, score in results:
        doc = next(d for d in documents if d.id == doc_id)
        response_results.append({
            "document_id": doc.id,
            "title": doc.title,
            "url": doc.url,
            "snippet": doc.content[:150],
            "score": score,
        })

    db.close()

    result = {
        "query": q,
        "algorithm": algorithm,
        "total": len(response_results),
        "results": response_results,
        "cached": False,
    }

    # Store the result in Redis for next time.
    # json.dumps converts the Python dict into a string, since Redis stores strings.
    # ex=300 means this entry expires automatically after 300 seconds (5 minutes) --
    # so if documents change later, stale results don't stick around forever.
    redis_client.set(cache_key, json.dumps(result), ex=300)

    return result