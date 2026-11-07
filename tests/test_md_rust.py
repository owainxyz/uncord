import io
import random
import re
import unittest
from types import SimpleNamespace

from rich.console import Console

from tests import oracle_md
from uncord import fmt

CASES = [
    "", "lol", "  spaced  ", "a\nb", "\nlead", "trail\n\n", "> q", ">", "> ", ">>> multi\nline\n> x", "# H", "## H2",
    "### H3", "#### not", "-# small", "- a\n* b", "  - indented", "1. x", "12. twelve", "1234. no",
    "**b** *i* _u_ __u__ ~~s~~ ||sp||", "***bi*** **b *i* b**", "`c` ``d`` ```inline```", "`` ` ``",
    "https://x.com/a?b=1.", "https://www.youtube.com/watch?v=abc&t=10s", "<https://a.b/c>",
    "[t](https://e.com)", "[discord.com](https://evil.com/x)", "[x](<https://e.com/y>)",
    "https://cdn.discordapp.com/attachments/1/2/file.png", "https://dіscord.com/gift", "https://xn--dscord-3ve.com",
    "https://example.com/" + "a" * 60, "<@1> <@!2> <@&3> <@&4> <#5> <#6> </cmd sub:7> @everyone @here",
    "<t:1700000000> <t:1700000000:R> <t:1700000000:t> <t:99999999999999999999:R> <t:-5:D>",
    "<:pog:123> <a:dance:456>", "a_b_c snake_case _ital_ x_y_", "x * y * z", "*not italic *", "**unclosed",
    "||**bold spoiler** <@1>||", "||" + "x" * 80 + "||", "> **quoted** https://e.com", "# **head** link https://e.com",
    "日本語 **太字** café ß 😀 <@1>", "tab\there", "line1\r\nline2", "~~~~", "____", "**", "||||",
]
ALPHABET = list("ab *_~`|[]()<>@#:/.-\n") + ["https://", "<@1>", "<#5>", "<@&3>", "||", "**", "`", "> ", "- ",
                                            "<t:1700000000:R>", "日", "é", "[l](https://e.com)", "<:e:1>"]


def ctx(reveal):
    users = {1: SimpleNamespace(id=1, display_name="me"), 2: SimpleNamespace(id=2, display_name="bob")}
    roles = {3: SimpleNamespace(name="mods", colour=SimpleNamespace(value=0xF23F43, __str__=lambda s: "#f23f43"))}

    class Colour:
        value = 0xF23F43

        def __str__(self):
            return "#f23f43"

    roles[3] = SimpleNamespace(name="mods", colour=Colour())
    channels = {5: SimpleNamespace(name="general")}
    return fmt.MdContext(1, users, roles, channels.get, reveal)


LINK_ID = re.compile(r"id=\d+")


def ansi(text):
    con = Console(width=100, file=io.StringIO(), force_terminal=True, color_system="truecolor", legacy_windows=False)
    con.print(text, end="")
    return LINK_ID.sub("id=x", con.file.getvalue())


class RustMarkdownTest(unittest.TestCase):

    def check(self, text):
        for reveal in (False, True):
            c = ctx(reveal)
            new = fmt.markdown(text, c)
            try:
                old = oracle_md.markdown(text, c)
            except ValueError:
                continue
            self.assertEqual(new.plain, old.plain, repr(text))
            self.assertEqual(ansi(new), ansi(old), repr(text))

    def testCases(self):
        for text in CASES:
            self.check(text)

    def testRandom(self):
        random.seed(7)
        for _ in range(1500):
            self.check("".join(random.choices(ALPHABET, k=random.randint(1, 25))))

    def testInlineWithBase(self):
        from rich.style import Style

        c = ctx(False)
        for base in (Style(), Style(bold=True), Style(dim=True, color="red")):
            for text in CASES[:30]:
                self.assertEqual(ansi(fmt.mdInline(text, c, base)), ansi(oracle_md.mdInline(text, c, base)), repr(text))

    def testShortUrl(self):
        for url in ("https://www.youtube.com/watch?v=x", "https://cdn.discordapp.com/attachments/1/2/a.png",
                    "https://discord.com/attachments/1/2/", "https://e.com/" + "é" * 50, "https://e.com/a/#frag",
                    "https://google.com/search?q=1#x", "http://a", "https://user@host:8080/p?q"):
            self.assertEqual(fmt.shortUrl(url), oracle_md.shortUrl(url), url)


if __name__ == "__main__":
    unittest.main()
