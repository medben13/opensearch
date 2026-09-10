from app.search.spellcheck import levenshtein_distance, find_closest_word


def test_levenshtein_identical_words():
    assert levenshtein_distance("computer", "computer") == 0


def test_levenshtein_one_substitution():
    assert levenshtein_distance("cat", "bat") == 1


def test_levenshtein_insertion():
    assert levenshtein_distance("cat", "cats") == 1


def test_levenshtein_deletion():
    assert levenshtein_distance("cats", "cat") == 1


def test_find_closest_word_corrects_typo():
    vocabulary = {"computer", "science", "engineering"}
    result = find_closest_word("comptuer", vocabulary)
    assert result == "computer"


def test_find_closest_word_returns_exact_match_unchanged():
    vocabulary = {"computer", "science"}
    result = find_closest_word("computer", vocabulary)
    assert result == "computer"


def test_find_closest_word_returns_none_when_too_different():
    vocabulary = {"computer", "science"}
    result = find_closest_word("xyz123", vocabulary)
    assert result is None