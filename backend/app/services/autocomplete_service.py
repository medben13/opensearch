from app.search.trie import Trie
from app.search.tokenizer import tokenize


def build_trie_from_documents(documents: list) -> Trie:
    """
    Builds a Trie containing every unique word across all documents,
    so autocomplete suggestions come from real, searchable vocabulary.
    """
    trie = Trie()
    seen_words = set()

    for doc in documents:
        tokens = tokenize(doc.content)
        for token in tokens:
            if token not in seen_words:
                trie.insert(token)
                seen_words.add(token)

    return trie