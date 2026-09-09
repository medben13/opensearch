from collections import defaultdict
from app.search.tokenizer import tokenize


class InvertedIndex:
    """
    Maps each word (token) to the set of document IDs that contain it.
    """

    def __init__(self):
        self.index: dict[str, set[int]] = defaultdict(set)
        self.documents: dict[int, str] = {}
        self.doc_tokens: dict[int, list[str]] = {}

    def add_document(self, doc_id: int, text: str) -> None:
        """
        Tokenizes a document's text and records which document each token appears in.
        Also precomputes and stores the token list, so search doesn't have to
        re-tokenize this document's text every time it matches a query.
        """
        self.documents[doc_id] = text
        tokens = tokenize(text)
        self.doc_tokens[doc_id] = tokens

        for token in tokens:
            self.index[token].add(doc_id)

    def get_documents_for_term(self, term: str) -> set[int]:
        """
        Returns the set of document IDs containing this single term.
        """
        normalized = tokenize(term)
        if not normalized:
            return set()
        return self.index.get(normalized[0], set())

    def build_from_documents(self, documents: list) -> None:
        """
        Rebuilds the index from a list of Document objects (from the database).
        Each Document has .id and .content attributes.
        """
        self.index.clear()
        self.documents.clear()
        self.doc_tokens.clear()

        for doc in documents:
            self.add_document(doc.id, doc.content)