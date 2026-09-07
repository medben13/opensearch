from app.search.tokenizer import tokenize
from app.search.index import InvertedIndex


def basic_search(index: InvertedIndex, query: str) -> set[int]:
    """
    Returns the set of document IDs that contain ALL words in the query
    (an AND search). No ranking yet -- just which documents match.
    """
    query_terms = tokenize(query)

    if not query_terms:
        return set()

    # Start with the documents matching the FIRST term
    result_docs = index.get_documents_for_term(query_terms[0])

    # For every other term, keep only documents that ALSO appear in that term's set
    for term in query_terms[1:]:
        term_docs = index.get_documents_for_term(term)
        result_docs = result_docs.intersection(term_docs)

    return result_docs