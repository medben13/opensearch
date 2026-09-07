from app.search.tokenizer import tokenize
from app.search.index import InvertedIndex
from app.search.tfidf import compute_idf


def bm25_search(
    index: InvertedIndex,
    query: str,
    k1: float = 1.2,
    b: float = 0.75,
) -> list[tuple[int, float]]:
    """
    Scores every matching document using BM25 and returns them
    sorted best-match-first.
    """
    query_terms = tokenize(query)
    scores: dict[int, float] = {}

    # Precompute document lengths and the average length across the collection.
    # We need avgdl before scoring any single document, so this must happen first.
    doc_lengths: dict[int, int] = {}
    for doc_id, text in index.documents.items():
        doc_lengths[doc_id] = len(tokenize(text))

    if not doc_lengths:
        return []

    avgdl = sum(doc_lengths.values()) / len(doc_lengths)

    for term in query_terms:
        matching_docs = index.get_documents_for_term(term)
        idf = compute_idf(term, index)

        for doc_id in matching_docs:
            doc_tokens = tokenize(index.documents[doc_id])
            f = doc_tokens.count(term)  # raw term frequency, unlike TF-IDF's normalized version
            dl = doc_lengths[doc_id]

            numerator = f * (k1 + 1)
            denominator = f + k1 * (1 - b + b * (dl / avgdl))

            term_score = idf * (numerator / denominator)
            scores[doc_id] = scores.get(doc_id, 0.0) + term_score

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return ranked