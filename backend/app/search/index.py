from collections import defaultdict
from app.search.tokenizer import tokenize


class InvertedIndex:
    """
    Maps each word (token) to the set of document IDs that contain it.
    """

    def __init__(self):
        # defaultdict(set) means: if we look up a word that isn't in the
        # dictionary yet, it automatically creates an empty set for it
        # instead of raising a KeyError. This avoids writing "if word not
        # in index: index[word] = set()" every time.
        self.index: dict[str, set[int]] = defaultdict(set)

        # Keep the original document text too, so we can show snippets/titles later
        self.documents: dict[int, str] = {}

    def add_document(self, doc_id: int, text: str) -> None:
        """
        Tokenizes a document's text and records which document each token appears in.
        """
        self.documents[doc_id] = text
        tokens = tokenize(text)

        for token in tokens:
            self.index[token].add(doc_id)

    def get_documents_for_term(self, term: str) -> set[int]:
        """
        Returns the set of document IDs containing this single term.
        """
        # tokenize the term too, so searching "Computer" matches the same
        # way "computer" was indexed
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

        for doc in documents:
            self.add_document(doc.id, doc.content)