import asyncio
import unittest

from textual.app import App
from textual.widgets import Input

from uncord import config, plugins, settings


class Stub(App):

    def __init__(self):
        super().__init__()
        self.cfg = config.Config()
        self.cfg.save = lambda: None
        self.client = type("Client", (), {"user": None})()
        self.notes = []

    def plugin(self, key):
        return plugins.enabled(self.cfg, key)

    def pluginChanged(self, key):
        pass

    def stopMicTest(self):
        pass

    def notify(self, message, **kw):
        self.notes.append(message)

    def on_mount(self):
        self.push_screen(settings.SettingsScreen("plugins"))


class PluginSettingsTest(unittest.TestCase):

    def testPluginInputsSave(self):
        async def run():
            app = Stub()
            async with app.run_test(size=(120, 45)) as pilot:
                await pilot.pause()
                swaps = app.screen.query_one("#in-pl-text_replace", Input)
                words = app.screen.query_one("#in-pl-keyword_notify", Input)
                swaps.value = "idk => i don't know; tbh => to be honest"
                swaps.focus()
                await pilot.press("enter")
                words.value = "Uncord, nix"
                words.focus()
                await pilot.press("enter")
                await pilot.pause()
                return dict(app.cfg["text_replace"]), list(app.cfg["keywords"])

        swaps, words = asyncio.run(run())
        self.assertEqual(swaps, {"idk": "i don't know", "tbh": "to be honest"})
        self.assertEqual(words, ["uncord", "nix"])


if __name__ == "__main__":
    unittest.main()
