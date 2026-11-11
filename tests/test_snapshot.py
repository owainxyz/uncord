import os
import tempfile
import unittest
from unittest import mock

from rich.text import Text

from uncord import icons, snapshot


class SnapshotTest(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.env = mock.patch.dict(os.environ, {"UNCORD_CACHE_DIR": self.dir})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def testRoundTripIsPrivate(self):
        ansi = snapshot.toAnsi(Text("hi", style="bold"), 40)
        snapshot.save({"channel": 1, "title": "# general", "sidebar": [[0, "Server", False, True]], "messages": [ansi]})
        self.assertEqual(os.stat(snapshot.path()).st_mode & 0o777, 0o600)
        data = snapshot.load()
        self.assertEqual(data["channel"], 1)
        self.assertEqual(Text.from_ansi(data["messages"][0]).plain, "hi")

    def testLinesAreNotPadded(self):
        from rich.table import Table

        grid = Table.grid(expand=True)
        grid.add_column(width=5)
        grid.add_column(ratio=1)
        grid.add_row("12:00", Text("hello\nthere", style="bold"))
        ansi = snapshot.toAnsi(grid, 60)
        self.assertEqual(Text.from_ansi(ansi).plain, "12:00hello\n     there")
        self.assertEqual(snapshot.tidy(ansi), ansi)
        self.assertEqual(snapshot.tidy("a   \n\x1b[1mb\x1b[0m  \x1b[0m\n\n"), "a\n\x1b[1mb\x1b[0m")

    def testForgetAndBadFiles(self):
        snapshot.save({"channel": 1})
        snapshot.forget()
        self.assertIsNone(snapshot.load())
        snapshot.path().write_text("not json")
        self.assertIsNone(snapshot.load())
        snapshot.path().write_text('{"v": 0}')
        self.assertIsNone(snapshot.load())


class IconTest(unittest.TestCase):

    def tearDown(self):
        icons.setStyle("auto")

    def testStyles(self):
        icons.setStyle("emoji")
        self.assertEqual(icons.icon("settings"), "⚙")
        icons.setStyle("nerd")
        self.assertEqual(icons.icon("settings"), "")
        icons.setStyle("bogus")
        self.assertEqual(icons._style, "auto")


if __name__ == "__main__":
    unittest.main()
