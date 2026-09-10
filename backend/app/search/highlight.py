import re


def highlight_terms(text: str, query_terms: list[str]) -> str:
    """
    Wraps every occurrence of any query term in `text` with <mark> tags,
    for the frontend to visually highlight. Case-insensitive matching,
    but preserves the original text's casing in the output.
    """
    if not query_terms:
        return text

    # Build one regex pattern matching ANY of the query terms, as whole
    # words only (\b = word boundary, so "cat" doesn't match inside "category").
    # re.escape() ensures special regex characters in a term (like '.' or '*')
    # are treated as literal characters, not regex syntax.
    escaped_terms = [re.escape(term) for term in query_terms]
    pattern = r"\b(" + "|".join(escaped_terms) + r")\b"

    def wrap_match(match: re.Match) -> str:
        return f"<mark>{match.group(0)}</mark>"

    highlighted = re.sub(pattern, wrap_match, text, flags=re.IGNORECASE)
    return highlighted