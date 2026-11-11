import unittest
from datetime import datetime

from uncord import plugins


class TextReplaceTest(unittest.TestCase):

    def testWholeWordsOnly(self):
        self.assertEqual(plugins.textReplace("idk tbh, idkk", {"idk": "i don't know", "tbh": "to be honest"}),
                         "i don't know to be honest, idkk")

    def testReplacementIsLiteral(self):
        self.assertEqual(plugins.textReplace("a", {"a": r"\1 \g<0>"}), r"\1 \g<0>")

    def testParseRules(self):
        self.assertEqual(plugins.parseRules("idk => i dont know; tbh=>to be honest; bad; =>x"),
                         {"idk": "i dont know", "tbh": "to be honest"})
        self.assertEqual(len(plugins.parseRules(";".join(f"w{i} => x" for i in range(500)))), plugins.MAX_RULES)

    def testFormatRoundTrip(self):
        rules = {"idk": "i don't know", "brb": "be right back"}
        self.assertEqual(plugins.parseRules(plugins.formatRules(rules)), rules)


class SendTimestampsTest(unittest.TestCase):

    now = datetime(2026, 11, 7, 20, 0).astimezone()

    def stamp(self, text):
        return plugins.sendTimestamps(text, self.now)

    def testPastTimeMeansTomorrow(self):
        out = self.stamp("<t:18:30>")
        self.assertRegex(out, r"^<t:\d+:t>$")
        self.assertGreater(int(out[3:-3]), self.now.timestamp())

    def testRelative(self):
        self.assertEqual(self.stamp("<t:+2h>"), f"<t:{int(self.now.timestamp()) + 7200}:R>")

    def testDate(self):
        self.assertRegex(self.stamp("<t:2026-12-25 09:00>"), r"^<t:\d+:f>$")

    def testLeavesRealAndInvalidAlone(self):
        for text in ("<t:1700000000:R>", "<t:25:00>", "<t:12:99>", "<t:2026-13-40 10:00>"):
            self.assertEqual(self.stamp(text), text)


class KeywordTest(unittest.TestCase):

    def testMatchesWholeWordsIgnoringCase(self):
        self.assertTrue(plugins.keywordHit("Anyone using UNCORD?", ["uncord"]))
        self.assertFalse(plugins.keywordHit("uncords", ["uncord"]))
        self.assertFalse(plugins.keywordHit("", ["uncord"]))
        self.assertFalse(plugins.keywordHit("uncord", []))

    def testParseKeywords(self):
        self.assertEqual(plugins.parseKeywords("Uncord, nix, , uncord"), ["uncord", "nix"])


class LinkPluginsTest(unittest.TestCase):

    def testFixEmbeds(self):
        self.assertEqual(plugins.fixEmbeds("https://x.com/a/status/1"), "https://fixupx.com/a/status/1")
        self.assertEqual(plugins.fixEmbeds("https://old.reddit.com/r/y"), "https://rxddit.com/r/y")
        for url in ("https://xx.com/z", "https://twitter.com:8080/q", "https://example.com"):
            self.assertEqual(plugins.fixEmbeds(url), url)

    def testClearUrls(self):
        self.assertEqual(plugins.clearUrls("https://e.com/?utm_source=a&id=1"), "https://e.com/?id=1")
        self.assertEqual(plugins.clearUrls("https://youtu.be/x?si=abc&t=5"), "https://youtu.be/x?t=5")
        self.assertEqual(plugins.clearUrls("https://e.com/?si=keep"), "https://e.com/?si=keep")


class SplitTest(unittest.TestCase):

    def testShortIsUntouched(self):
        self.assertEqual(plugins.splitMessage("hi"), ["hi"])
        self.assertEqual(plugins.splitMessage("x" * 2000), ["x" * 2000])

    def testCutsAtLinesAndWords(self):
        text = "\n".join(f"line {i} " + "word " * 20 for i in range(80))
        parts = plugins.splitMessage(text)
        self.assertGreater(len(parts), 1)
        self.assertTrue(all(0 < len(p) <= 2000 for p in parts))
        self.assertEqual("".join(parts).split(), text.split())

    def testOneLongWord(self):
        parts = plugins.splitMessage("x" * 5000)
        self.assertTrue(all(len(p) <= 2000 for p in parts))
        self.assertEqual("".join(parts), "x" * 5000)

    def testCodeBlockIsClosedAndReopened(self):
        code = "\n".join(f"print({i})" for i in range(400))
        parts = plugins.splitMessage(f"look\n```py\n{code}\n```\ndone")
        self.assertGreater(len(parts), 1)
        for p in parts:
            self.assertLessEqual(len(p), 2000)
            self.assertEqual(p.count("```") % 2, 0)
        self.assertTrue(parts[1].startswith("```py\n"))
        kept = [line for p in parts for line in p.split("\n") if line.startswith("print(")]
        self.assertEqual(kept, code.split("\n"))


class RegistryTest(unittest.TestCase):

    def testKeysAreUnique(self):
        keys = [key for key, *_r in plugins.PLUGINS]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(set(plugins.DEFAULTS), set(keys))


if __name__ == "__main__":
    unittest.main()
