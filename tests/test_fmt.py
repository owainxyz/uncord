import unittest

from uncord import fmt


def render(text):
    return fmt.markdown(text, fmt.MdContext(1)).plain


class MarkdownTest(unittest.TestCase):

    def testPlainTextIsUntouched(self):
        for text in ("lol", "  spaced", "a\nb", "#notheading", "x * y", "a_b_c"):
            self.assertEqual(render(text), text.rstrip())

    def testInline(self):
        self.assertEqual(render("**b** *i* `c` ~~s~~"), "b i c s")
        self.assertEqual(render("||secret||"), "▒▒▒▒▒▒")

    def testBlocks(self):
        self.assertEqual(render("> quote"), "▎ quote")
        self.assertEqual(render("- a\n* b"), "• a\n• b")
        self.assertEqual(render("```py\nx = 1\n```"), "┏ py\n┃ x = 1")

    def testLinks(self):
        self.assertEqual(render("see https://github.com/owainxyz/uncord"), "see github.com/owainxyz/uncord")
        self.assertIn("⚠ goes to evil.com", render("[discord.com](https://evil.com/x)"))
        self.assertIn("⚠ lookalike link, really xn--dscord-pvf.com", render("https://dіscord.com/gift"))

    def testMentions(self):
        self.assertEqual(render("<@1> <#2> @everyone"), "@unknown-user #unknown @everyone")

    def testHighlightCacheReturnsCopies(self):
        a = fmt.highlight("x = 1", "py")
        a.append("changed")
        self.assertNotIn("changed", fmt.highlight("x = 1", "py").plain)


if __name__ == "__main__":
    unittest.main()
