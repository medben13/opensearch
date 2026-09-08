from fastapi import FastAPI
from app.core.database import SessionLocal
from app.services.document_service import get_all_documents
from app.search.index import InvertedIndex
from app.search.bm25 import bm25_search

app = FastAPI(title="OpenSearch API")


@app.get("/api/v1/search")
def search(q: str):
    """
    Handles GET /api/v1/search?q=<query>
    Returns matching documents ranked by BM25 relevance.
    """
    db = SessionLocal()
    documents = get_all_documents(db)

    index = InvertedIndex()
    index.build_from_documents(documents)

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
        "total": len(response_results),
        "results": response_results,
    }