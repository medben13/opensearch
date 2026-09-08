from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import SessionLocal
from app.services.document_service import get_all_documents
from app.search.index import InvertedIndex
from app.search.bm25 import bm25_search
from app.search.tfidf import tfidf_search

app = FastAPI(title="OpenSearch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

6
@app.get("/api/v1/search")
def search(q: str, algorithm: str = "bm25"):
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

    return {
        "query": q,
        "algorithm": algorithm,
        "total": len(response_results),
        "results": response_results,
    }


@app.get("/api/v1/documents/{document_id}")
def get_document(document_id: int):
    """
    Returns a single document's full details by ID.
    """
    db = SessionLocal()
    documents = get_all_documents(db)
    db.close()

    doc = next((d for d in documents if d.id == document_id), None)

    if doc is None:
        # HTTPException is FastAPI's way of returning a proper error status code,
        # instead of a 200 OK with confusing/empty content
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
    """
    Returns basic statistics about the indexed collection.
    """
    db = SessionLocal()
    documents = get_all_documents(db)
    db.close()

    return {
        "total_documents": len(documents),
    }


@app.post("/api/v1/crawl")
def crawl():
    """
    Placeholder for now -- will trigger the crawler once we build it (Step 15).
    """
    return {"status": "Crawler not implemented yet"}