from collections import deque

class AhoCorasick:
    def __init__(self, patterns):
        self.trie = [{"next": {}, "fail": 0, "output": []}]
        self._build_trie(patterns)
        self._build_failure_links()

    def _build_trie(self, patterns):
        for pattern in patterns:
            node = 0
            for ch in pattern:
                if ch not in self.trie[node]["next"]:
                    self.trie[node]["next"][ch] = len(self.trie)
                    self.trie.append({"next": {}, "fail": 0, "output": []})
                node = self.trie[node]["next"][ch]
            self.trie[node]["output"].append(pattern)

    def _build_failure_links(self):
        queue = deque()

        # First layer: fail -> root
        for ch, nxt in self.trie[0]["next"].items():
            self.trie[nxt]["fail"] = 0
            queue.append(nxt)

        # BFS
        while queue:
            r = queue.popleft()
            for ch, u in self.trie[r]["next"].items():
                queue.append(u)

                f = self.trie[r]["fail"]
                while f != 0 and ch not in self.trie[f]["next"]:
                    f = self.trie[f]["fail"]

                if ch in self.trie[f]["next"]:
                    self.trie[u]["fail"] = self.trie[f]["next"][ch]
                else:
                    self.trie[u]["fail"] = 0

                self.trie[u]["output"].extend(
                    self.trie[self.trie[u]["fail"]]["output"]
                )

    def search(self, text):
        node = 0
        matches = []

        for i, ch in enumerate(text):
            while node != 0 and ch not in self.trie[node]["next"]:
                node = self.trie[node]["fail"]

            if ch in self.trie[node]["next"]:
                node = self.trie[node]["next"][ch]
            else:
                node = 0

            for pattern in self.trie[node]["output"]:
                start = i - len(pattern) + 1
                matches.append((pattern, start, i))

        return matches


patterns = ["new", "anti", "group"]
text = "A new group of antifungal and antibacterial lipopeptides derived from non-membrane active peptides"

ac = AhoCorasick(patterns)
results = ac.search(text)

for pattern, start, end in results:
    print(f"Found '{pattern}' at text[{start}:{end+1}] -> '{text[start:end+1]}'")



