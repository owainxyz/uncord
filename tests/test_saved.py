import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from uncord import commands, saved


class Cfg(dict):

    def save(self):
        self.saves = getattr(self, "saves", 0) + 1


def message(i, content="hello   there\x1b[31m", files=()):
    return SimpleNamespace(id=i, content=content, attachments=list(files), guild=None,
                           channel=SimpleNamespace(id=9), author=SimpleNamespace(display_name="Bob"),
                           created_at=datetime(2026, 11, 11, tzinfo=timezone.utc))


class SavedTest(unittest.TestCase):

    def testEntryIsCleanAndShort(self):
        e = saved.entry(message(1, "x" * 500))
        self.assertEqual(len(e["text"]), saved.MAX_TEXT)
        self.assertEqual(saved.entry(message(2))["text"], "hello there[31m")
        self.assertEqual(saved.entry(message(3, "", [SimpleNamespace(filename="cat.png")]))["text"], "cat.png")

    def testToggle(self):
        cfg = Cfg()
        self.assertTrue(saved.toggle(cfg, saved.entry(message(1))))
        self.assertTrue(saved.toggle(cfg, saved.entry(message(2))))
        self.assertEqual([e["id"] for e in saved.saved(cfg)], [2, 1])
        self.assertTrue(saved.isSaved(cfg, 1))
        self.assertFalse(saved.toggle(cfg, saved.entry(message(1))))
        self.assertFalse(saved.isSaved(cfg, 1))
        self.assertEqual(cfg.saves, 3)

    def testCapAndBadEntries(self):
        cfg = Cfg(saved=["junk", {"id": "1"}, {"id": 5, "channel": 9}])
        self.assertEqual([e["id"] for e in saved.saved(cfg)], [5])
        for i in range(saved.MAX_SAVED + 20):
            saved.toggle(cfg, saved.entry(message(100 + i)))
        self.assertEqual(len(saved.saved(cfg)), saved.MAX_SAVED)


class TextCommandTest(unittest.TestCase):

    def testFacesAndWraps(self):
        self.assertEqual(commands.textCommand("shrug", "idk"), "idk ¯\\\\_(ツ)\\_/¯")
        self.assertEqual(commands.textCommand("tableflip", ""), "(╯°□°)╯︵ ┻━┻")
        self.assertEqual(commands.textCommand("me", "waves"), "_waves_")
        self.assertEqual(commands.textCommand("spoiler", "it was him"), "||it was him||")
        self.assertIsNone(commands.textCommand("me", ""))
        self.assertIsNone(commands.textCommand("join", ""))


if __name__ == "__main__":
    unittest.main()
