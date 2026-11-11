#ui icons: nerd font glyphs when a nerd font is installed, the old emoji otherwise
from __future__ import annotations

import shutil
import subprocess
from functools import lru_cache

#name: (nerd font glyph, emoji)
ICONS = {
    "settings": ("", "⚙"),
    "mic": ("", "🎙"),
    "micOff": ("", "🔇"),
    "headphones": ("", "🎧"),
    "deafened": ("\U000f07ce", "🙉"),
    "leave": ("", "✆"),
    "voice": ("", "🔊"),
    "muted": ("", "🔇"),
    "screen": ("", "🖥"),
    "camera": ("", "📷"),
    "live": ("", "🔴"),
    "watching": ("", "📺"),
    "reply": ("", "↪"),
    "react": ("", "☺"),
    "edit": ("", "✎"),
    "delete": ("", "🗑"),
    "play": ("", "▶"),
    "jump": ("", "↩"),
    "copy": ("", "⧉"),
    "link": ("", "🔗"),
    "thread": ("", "🧵"),
    "pin": ("", "📌"),
    "message": ("", "✉"),
    "profile": ("", "👤"),
    "translate": ("", "🌐"),
    "search": ("", "🔍"),
    "attachment": ("", "📎"),
    "emoji": ("", "☺"),
    "id": ("", "⧉"),
    "raw": ("", "{ }"),
    "status": ("", "✎"),
    "bookmark": ("\uf02e", "🔖"),
    "forward": ("\uf064", "↪"),
}

STYLES = ("auto", "nerd", "emoji")
_style = "auto"


@lru_cache(maxsize=1)
def nerdFontInstalled() -> bool:
    fc = shutil.which("fc-list")
    if not fc:
        return False
    try:
        out = subprocess.run([fc, ":", "family"], capture_output=True, text=True, timeout=3).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return "nerd font" in out.lower() or " nf" in out.lower()


def setStyle(style: str) -> None:
    global _style
    _style = style if style in STYLES else "auto"


def useNerd() -> bool:
    return _style == "nerd" or (_style == "auto" and nerdFontInstalled())


def icon(name: str) -> str:
    nerd, emoji = ICONS[name]
    return nerd if useNerd() else emoji
