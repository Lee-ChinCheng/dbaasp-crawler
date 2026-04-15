import ahocorasick #pip install pyahocorasick

A = ahocorasick.Automaton()
patterns = ["new", "anti", "group"]

for idx, pat in enumerate(patterns):
    A.add_word(pat, (idx, pat))

A.make_automaton()

text = "A new group of antifungal and antibacterial lipopeptides derived from non-membrane active peptides"

for end_idx, (_, pat) in A.iter(text):
    start_idx = end_idx - len(pat) + 1
    print(f"Found '{pat}' at text[{start_idx}:{end_idx+1}]")