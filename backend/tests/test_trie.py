from app.search.trie import Trie


def test_trie_returns_matching_prefix():
    trie = Trie()
    trie.insert("computer")
    trie.insert("computing")
    trie.insert("compiler")
    trie.insert("science")

    results = trie.get_suggestions("comp")
    assert set(results) == {"computer", "computing", "compiler"}


def test_trie_respects_limit():
    trie = Trie()
    for word in ["cat", "car", "card", "care", "cart"]:
        trie.insert(word)

    results = trie.get_suggestions("car", limit=2)
    assert len(results) == 2


def test_trie_returns_empty_for_no_match():
    trie = Trie()
    trie.insert("computer")

    results = trie.get_suggestions("xyz")
    assert results == []


def test_trie_prefix_that_is_also_a_word():
    trie = Trie()
    trie.insert("compute")
    trie.insert("computer")

    results = trie.get_suggestions("compute")
    assert set(results) == {"compute", "computer"}