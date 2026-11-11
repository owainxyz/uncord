#messages you saved with b, kept in the config so /saved can jump back to them
from __future__ import annotations

from .safety import clean

MAX_SAVED = 200
MAX_TEXT = 120


def entry(m) -> dict:
    guild = getattr(m, "guild", None)
    text = " ".join(clean(m.content or "").split())
    snaps = getattr(m, "message_snapshots", None) or ()
    if not text and snaps:
        text = " ".join(clean(snaps[0].content or "").split())
    files = list(m.attachments) + [a for s in snaps for a in s.attachments]
    if not text and files:
        text = clean(files[0].filename)
    return {"id": m.id, "channel": m.channel.id, "guild": guild.id if guild is not None else None,
            "author": clean(m.author.display_name)[:64], "text": text[:MAX_TEXT], "at": int(m.created_at.timestamp())}


def _valid(e) -> bool:
    return isinstance(e, dict) and isinstance(e.get("id"), int) and isinstance(e.get("channel"), int)


def saved(cfg) -> list:
    return [e for e in cfg.get("saved") or [] if _valid(e)]


def isSaved(cfg, messageId: int) -> bool:
    return any(e["id"] == messageId for e in saved(cfg))


#true if its saved now, false if that took it off the list
def toggle(cfg, e: dict) -> bool:
    items = saved(cfg)
    kept = [x for x in items if x["id"] != e["id"]]
    on = len(kept) == len(items)
    if on:
        kept = ([e] + kept)[:MAX_SAVED]
    cfg["saved"] = kept
    cfg.save()
    return on
