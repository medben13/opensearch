from app.search.index import InvertedIndex
from app.search.bm25 import bm25_search


def test_bm25_ranks_relevant_document_higher():
    idx = InvertedIndex()
    # doc 1 mentions "computer" heavily and is short -> should rank higher
    idx.add_document(1, "computer computer computer")
    # doc 2 barely mentions "computer" and is longer -> should rank lower
    idx.add_document(2, "computer science engineering university research topics")

    results = bm25_search(idx, "computer")
    ranked_doc_ids = [doc_id for doc_id, score in results]

    assert ranked_doc_ids[0] == 1


def test_bm25_returns_empty_list_for_empty_index():
    idx = InvertedIndex()
    results = bm25_search(idx, "computer")
    assert results == []