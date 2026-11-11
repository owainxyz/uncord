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


class ForwardTest(unittest.TestCase):

    def testForwardedMessageShowsItsTextAndFiles(self):
        import io

        import discord
        from rich.console import Console

        from uncord import media

        state = discord.Client()._connection
        user = {"id": "5", "username": "bob", "discriminator": "0", "global_name": "Bob", "avatar": None}
        channel = discord.DMChannel(me=None, state=state, data={"id": "9", "type": 1, "recipients": [user],
                                                                "last_message_id": None})
        url = "https://cdn.discordapp.com/attachments/1/2/cat.png"
        file = {"id": "77", "filename": "cat.png", "size": 12345, "url": url, "content_type": "image/png",
                "proxy_url": "https://media.discordapp.net/attachments/1/2/cat.png", "width": 100, "height": 80}
        snap = {"content": "**look** at this\nsecond line", "timestamp": "2026-11-10T10:00:00+00:00",
                "edited_timestamp": None, "attachments": [file], "embeds": [], "type": 0, "flags": 0,
                "mentions": [], "mention_roles": []}
        m = discord.Message(state=state, channel=channel, data={
            "id": "100", "channel_id": "9", "author": user, "content": "", "edited_timestamp": None,
            "timestamp": "2026-11-11T10:00:00+00:00", "tts": False, "mention_everyone": False, "mentions": [],
            "mention_roles": [], "attachments": [], "embeds": [], "pinned": False, "type": 0,
            "message_reference": {"type": 1, "channel_id": "8", "message_id": "50"},
            "message_snapshots": [{"message": snap}]})
        con = Console(width=60, file=io.StringIO())
        con.print(fmt.renderMessage(m, 1, lambda i: None))
        lines = [line.strip() for line in con.file.getvalue().split("\n")]
        self.assertEqual(lines[1:5], ["↪ forwarded", "▎ look at this", "▎ second line", "▎ 🖼 cat.png  12.1 KB"])
        self.assertEqual([it.url for it in media.itemsOf(m)], [url])


if __name__ == "__main__":
    unittest.main()
