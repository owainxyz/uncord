#what was on screen when you last quit, drawn straight away next time while discord connects
from __future__ import annotations

import io
import json
import logging
import os
import tempfile
from typing import Optional

from rich.console import Console

from .env import cacheDir
from .safety import private

log = logging.getLogger("uncord")

VERSION = 2
MAX_MESSAGES = 40
MAX_NODES = 400


def path():
    return cacheDir() / "snapshot.json"


def toAnsi(renderable, width: int) -> str:
    con = Console(width=max(20, width), file=io.StringIO(), force_terminal=True, color_system="truecolor",
                  legacy_windows=False, emoji=False, highlight=False)
    con.print(renderable, end="")
    return con.file.getvalue()


def save(data: dict) -> None:
    try:
        d = cacheDir()
        private(d, isDir=True)
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".snapshot-")
        with os.fdopen(fd, "w") as f:
            json.dump({"v": VERSION, **data}, f)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path())
    except OSError:
        log.debug("saving snapshot", exc_info=True)


def load() -> Optional[dict]:
    p = path()
    try:
        if p.is_symlink() or p.stat().st_uid != os.getuid():
            return None
        data = json.loads(p.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("v") != VERSION:
        return None
    return data


def forget() -> None:
    try:
        path().unlink()
    except OSError:
        pass
