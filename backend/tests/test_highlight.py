from app.search.highlight import highlight_terms


def test_highlight_wraps_matching_term():
    result = highlight_terms("Computer science is fun", ["computer"])
    assert result == "<mark>Computer</mark> science is fun"


def test_highlight_multiple_terms():
    result = highlight_terms("Computer science", ["computer", "science"])
    assert result == "<mark>Computer</mark> <mark>science</mark>"


def test_highlight_does_not_match_partial_word():
    result = highlight_terms("category theory", ["cat"])
    assert result == "category theory"  # "cat" should NOT match inside "category"


def test_highlight_empty_terms_returns_original():
    result = highlight_terms("Computer science", [])
    assert result == "Computer science"