import re

# A small set of common English words that carry little search value.
# Using a set (not a list) makes checking "is this word a stop word?" very fast.
STOP_WORDS = {
    "a", "an", "the", "is", "of", "to", "in", "and", "or", "on", "for",
    "with", "as", "by", "at", "it", "this", "that", "be", "are", "was",
}


def tokenize(text: str) -> list[str]:
    """
    Turns raw text into a clean list of searchable word tokens.

    Steps: lowercase -> extract words only -> remove stop words.
    """
    # Step 1: lowercase everything, so "Computer" and "computer" are treated the same
    text = text.lower()

    # Step 2: extract only sequences of letters/numbers, throwing away punctuation.
    # \w+ means "one or more letter, digit, or underscore characters."
    # re.findall returns every match as a list of strings.
    words = re.findall(r"\w+", text)

    # Step 3: drop stop words using a list comprehension
    tokens = [word for word in words if word not in STOP_WORDS]

    return tokens
    