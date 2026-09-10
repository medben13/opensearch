def levenshtein_distance(word1: str, word2: str) -> int:
    """
    Computes the minimum number of single-character edits (insertions,
    deletions, substitutions) needed to turn word1 into word2.
    """
    m, n = len(word1), len(word2)

    # dp[i][j] = edit distance between word1[:i] and word2[:j]
    # Build a (m+1) x (n+1) grid, since we need to represent the
    # "empty prefix" case (0 characters) too.
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: turning an empty string into a string of length j
    # takes j insertions; turning a string of length i into an empty
    # string takes i deletions.
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                # Characters match -- no new edit needed here, just
                # inherit the answer for one character shorter on both sides.
                dp[i][j] = dp[i - 1][j - 1]
            else:
                # Characters differ -- try all three possible edits and
                # take whichever leaves the smallest remaining distance:
                # deletion, insertion, substitution.
                dp[i][j] = 1 + min(
                    dp[i - 1][j],       # delete a character from word1
                    dp[i][j - 1],       # insert a character into word1
                    dp[i - 1][j - 1],   # substitute a character
                )

    return dp[m][n]


def find_closest_word(word: str, vocabulary: set[str], max_distance: int = 2) -> str | None:
    """
    Finds the vocabulary word with the smallest edit distance to `word`,
    among words within max_distance. Returns None if nothing is close enough.
    """
    if word in vocabulary:
        return word  # already a real word, no correction needed

    best_word = None
    best_distance = max_distance + 1

    for candidate in vocabulary:
        distance = levenshtein_distance(word, candidate)
        if distance < best_distance:
            best_distance = distance
            best_word = candidate

    if best_distance <= max_distance:
        return best_word
    return None