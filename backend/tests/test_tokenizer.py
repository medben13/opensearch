from app.search.tokenizer import tokenize


def test_tokenizer_lowercases_words():
    result = tokenize("COMPUTER")
    assert result == ["computer"]


def test_tokenizer_removes_punctuation():
    result = tokenize("Amazing!!!")
    assert result == ["amazing"]


def test_tokenizer_removes_stop_words():
    result = tokenize("this is a computer")
    # "this", "is", "a" are stop words and should be gone
    assert result == ["computer"]


def test_tokenizer_handles_empty_string():
    result = tokenize("")
    assert result == []


def test_tokenizer_matches_blueprint_example():
    result = tokenize("Computer Science is AMAZING!")
    assert result == ["computer", "science", "amazing"]