import math
from app.search.tokenizer import tokenize
from app.search.index import InvertedIndex


def compute_tf(term: str, doc_tokens: list[str]) -> float:
    """
    Term Frequency: how often `term` appears in this document,
    relative to the document's total length.
    """
    if not doc_tokens:
        return 0.0
    term_count = doc_tokens.count(term)
    return term_count / len(doc_tokens)


def compute_idf(term: str, index: InvertedIndex) -> float:
    """
    Inverse Document Frequency: how rare `term` is across ALL documents.
    Rare words score higher; common words score near zero.
    """
    n_docs = len(index.documents)
    doc_freq = len(index.get_documents_for_term(term))

    if doc_freq == 0:
        return 0.0

    return math.log(n_docs / doc_freq)


def tfidf_search(index: InvertedIndex, query: str) -> list[tuple[int, float]]:
    """
    Scores every document that matches ANY query term using TF-IDF,
    and returns them sorted best-match-first.
    """
    query_terms = tokenize(query)
    scores: dict[int, float] = {}

    for term in query_terms:
        matching_docs = index.get_documents_for_term(term)
        idf = compute_idf(term, index)

        for doc_id in matching_docs:
            doc_tokens = tokenize(index.documents[doc_id])
            tf = compute_tf(term, doc_tokens)

            # Add this term's contribution to the document's running score.
            # A document matching multiple query terms accumulates points from each.
            scores[doc_id] = scores.get(doc_id, 0.0) + (tf * idf)

    # Sort documents by score, highest first
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return ranked