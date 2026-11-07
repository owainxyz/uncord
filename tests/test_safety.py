import logging
import unittest

from uncord import safety


class LookalikeTest(unittest.TestCase):

    def testMixedScriptsAreFlagged(self):
        self.assertEqual(safety.lookalike("https://dіscord.com/gift"), "xn--dscord-pvf.com")
        self.assertEqual(safety.lookalike("https://xn--dscord-3ve.com/a"), "xn--dscord-3ve.com")

    def testWholeAlphabetFakes(self):
        self.assertEqual(safety.lookalike("https://аррӏе.com"), "xn--80ak6aa92e.com")
        self.assertEqual(safety.lookalike("https://xn--80ak6aa92e.com"), "xn--80ak6aa92e.com")

    def testRealForeignNamesPass(self):
        for url in ("https://дом.рф", "https://αβγ.gr"):
            self.assertIsNone(safety.lookalike(url))

    def testNormalHostsPass(self):
        for url in ("https://discord.com/x", "https://例え.jp", "https://xn--r8jz45g.jp", "not a url", ""):
            self.assertIsNone(safety.lookalike(url))


class UrlTest(unittest.TestCase):

    def testOnlyWebLinks(self):
        self.assertEqual(safety.safeUrl("https://e.com/a"), "https://e.com/a")
        for url in ("file:///etc/passwd", "javascript:alert(1)", "https://", "ftp://e.com", ""):
            self.assertIsNone(safety.safeUrl(url))

    def testDomain(self):
        self.assertEqual(safety.domain("https://www.github.com/x"), "github.com")


class CleanTest(unittest.TestCase):

    def testStripsControlsAndBidi(self):
        self.assertEqual(safety.clean("a\x1b]52;c;aGk=\x07b\u202ec\td\ne"), "a]52;c;aGk=bc\td\ne")


class RedactTest(unittest.TestCase):

    def fmt(self, msg, token=""):
        f = safety.RedactingFormatter("%(message)s", token)
        return f.format(logging.LogRecord("t", logging.INFO, "", 0, msg, None, None))

    def testTokensAndHeaders(self):
        fake = "MTIzNDU2Nzg5MDEyMzQ1Njc4.GaBcDe." + "x" * 38
        self.assertNotIn(fake, self.fmt(f"token {fake}"))
        self.assertEqual(self.fmt("Authorization: Bearer abc.def"), "Authorization: Bearer [token]")
        self.assertEqual(self.fmt("secret-value here", "secret-value"), "[token] here")


if __name__ == "__main__":
    unittest.main()
