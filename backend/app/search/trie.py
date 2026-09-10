class TrieNode:
    """
    One node in the Trie. Each node has children (one per possible next
    character) and a flag marking whether a complete word ends here.
    """
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end_of_word = False


class Trie:
    """
    A prefix tree supporting fast 'give me all words starting with X' lookups.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        Adds a word to the Trie, one character at a time, creating new
        nodes only where a path doesn't already exist.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def _collect_words(self, node: "TrieNode", prefix: str, results: list[str], limit: int) -> None:
        """
        Recursively walks every path below `node`, collecting complete
        words, stopping once `limit` results have been found.
        """
        if len(results) >= limit:
            return

        if node.is_end_of_word:
            results.append(prefix)

        for char, child_node in node.children.items():
            if len(results) >= limit:
                return
            self._collect_words(child_node, prefix + char, results, limit)

    def get_suggestions(self, prefix: str, limit: int = 10) -> list[str]:
        """
        Returns up to `limit` words in the Trie that start with `prefix`.
        """
        node = self.root
        prefix = prefix.lower()

        # Walk down to the node representing the end of the prefix.
        # If any character in the prefix has no matching child, nothing
        # in the Trie starts with this prefix -- return empty immediately.
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results: list[str] = []
        self._collect_words(node, prefix, results, limit)
        return results