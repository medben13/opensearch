from app.search.index import InvertedIndex


def test_index_returns_correct_documents():
    idx = InvertedIndex()
    idx.add_document(1, "Computer Science")
    idx.add_document(2, "Computer Engineering")

    assert idx.get_documents_for_term("computer") == {1, 2}
    assert idx.get_documents_for_term("science") == {1}


def test_index_returns_empty_set_for_unknown_term():
    idx = InvertedIndex()
    idx.add_document(1, "Computer Science")

    assert idx.get_documents_for_term("nonexistent") == set()