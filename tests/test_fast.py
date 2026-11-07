import random
import string
import unittest

from uncord import _fast


def pythonSearch(hays, q, limit=250):
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


class MatcherTest(unittest.TestCase):

    def testSameResultsAsPython(self):
        random.seed(5)
        alphabet = string.ascii_lowercase + "éß日本 -#"
        hays = ["".join(random.choices(alphabet, k=random.randint(0, 30))) for _ in range(3000)]
        m = _fast.Matcher(hays)
        for q in ("", "a", "ab", "a b", "é", "日本", "#", "zzzz", "ß-", "q w e"):
            self.assertEqual(m.search(q), pythonSearch(hays, q), q)
            self.assertEqual(m.search(q, 7), pythonSearch(hays, q, 7), q)

    def testEmpty(self):
        self.assertEqual(_fast.Matcher([]).search("a"), [])
        self.assertEqual(len(_fast.Matcher(["x", "y"])), 2)


if __name__ == "__main__":
    unittest.main()
