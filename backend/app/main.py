import json
import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import SessionLocal
from app.services.document_service import get_all_documents
from app.search.index import InvertedIndex
from app.search.tfidf import tfidf_search
from app.services.autocomplete_service import build_trie_from_documents

from app.search.bm25 import bm25_search
from app.search.pagerank import compute_pagerank
import os

app = FastAPI(title="OpenSearch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True,
)

PAGERANK_WEIGHT = 1000


@app.get("/api/v1/search")
def search(q: str, algorithm: str = "bm25"):
    cache_key = f"search:{algorithm}:{q}"

    cached_result = redis_client.get(cache_key)
    if cached_result is not None:
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

    pagerank_scores = compute_pagerank(db)

    combined_results = []
    for doc_id, relevance_score in results:
        pr_score = pagerank_scores.get(doc_id, 0.0)
        final_score = relevance_score + (pr_score * PAGERANK_WEIGHT)
        combined_results.append((doc_id, final_score))

    combined_results.sort(key=lambda x: x[1], reverse=True)
    results = combined_results

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

    redis_client.set(cache_key, json.dumps(result), ex=300)

    return result


@app.get("/api/v1/documents/{document_id}")
def get_document(document_id: int):
    db = SessionLocal()
    documents = get_all_documents(db)
    db.close()

    doc = next((d for d in documents if d.id == document_id), None)

    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": doc.id,
        "title": doc.title,
        "url": doc.url,
        "content": doc.content,
        "created_at": doc.created_at,
    }


@app.get("/api/v1/stats")
def stats():
    db = SessionLocal()
    documents = get_all_documents(db)
    db.close()

    return {
        "total_documents": len(documents),
    }


@app.post("/api/v1/crawl")
def crawl():
    return {"status": "Crawler not implemented yet"}
    

@app.get("/api/v1/autocomplete")
def autocomplete(prefix: str, limit: int = 10):
    """
    Returns word suggestions matching the given prefix.
    """
    if len(prefix) < 2:
        return {"prefix": prefix, "suggestions": []}

    db = SessionLocal()
    documents = get_all_documents(db)
    db.close()

    trie = build_trie_from_documents(documents)
    suggestions = trie.get_suggestions(prefix, limit=limit)

    return {"prefix": prefix, "suggestions": suggestions}    