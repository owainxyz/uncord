import random
import string
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from uncord import _fast


def pythonSearch(hays, q, limit=250):
    q = q.lower().strip()
    words = q.split()
    if not words:
        return list(range(min(len(hays), limit)))
    scored = []
    for i, hay in enumerate(hays):
        if all(w in hay for w in words):
            scored.append((hay.find(words[0]) + (0 if hay.startswith(words[0]) else 50), i))
        else:
            it = iter(hay)
            if all(c in it for c in q.replace(" ", "")):
                scored.append((1000 + len(hay), i))
    scored.sort()
    return [i for _s, i in scored[:limit]]


def corpus(n):
    random.seed(4)
    words = ["general", "memes", "voice", "gaming", "music", "dev", "nix", "uncord", "off-topic", "announcements",
             "café", "日本語", "rust", "linux", "art", "clips"]
    out = []
    for _ in range(n):
        name = "-".join(random.sample(words, 2)) + "".join(random.choices(string.ascii_lowercase, k=random.randint(0, 6)))
        out.append(f"# {name} {random.choice(words)} server")
    return out


def main(n=20000):
    hays = corpus(n)
    queries = ["g", "ge", "gen", "gener", "general", "gm", "nix dev", "unc", "café", "日本", "zzz"]
    m = _fast.Matcher(hays)
    for q in queries:
        assert m.search(q) == pythonSearch(hays, q), q
    for name, fn in (("python", lambda q: pythonSearch(hays, q)), ("rust", lambda q: m.search(q))):
        best = float("inf")
        for _ in range(3):
            start = time.perf_counter()
            for q in queries:
                fn(q)
            best = min(best, time.perf_counter() - start)
        print(f"picker search, {name}: {best * 1e3 / len(queries):.2f} ms per keystroke ({n} entries)")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20000)
