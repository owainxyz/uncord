#small optional tweaks in the spirit of vencord plugins, switched on and off with /plugins
from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

#key name what it does on by default
PLUGINS = (
    ("message_logger", "MessageLogger", "keep deleted messages and show what edited ones said before", True),
    ("show_usernames", "ShowMeYourName", "show @username next to nicknames", False),
    ("platform_icons", "PlatformIndicators", "show 🖥 📱 🌐 for the devices people are on", True),
    ("typing_indicator", "TypingIndicator", "✎ next to channels and DMs where someone is typing", True),
    ("call_timer", "CallTimer", "show how long you've been in a call", True),
    ("clear_urls", "ClearURLs", "strip tracking junk (utm, fbclid, si…) from links you send", True),
    ("fake_nitro", "FakeNitro", "send emoji you can't use here as image links instead of failing", True),
    ("no_reply_mention", "NoReplyMention", "replies don't ping the person you reply to", False),
    ("silent_typing", "SilentTyping", "don't show others that you're typing", False),
    ("relationship_notifier", "RelationshipNotifier", "tell you when someone unfriends you or sends a request", True),
    ("rich_presence", "RichPresence", "games and apps on this pc set your activity like the desktop app (restart after)", True),
    ("translate", "Translate", "translate messages from the message menu (enter or right click)", True),
    ("view_raw", "ViewRaw", "see a message's raw text and markdown from the message menu", True),
    ("who_reacted", "WhoReacted", "see who reacted with what from the message menu", True),
    ("reverse_image", "ReverseImageSearch", "search an image on google lens from the message menu", True),
    ("no_blocked", "NoBlockedMessages", "hide messages from people you blocked completely", False),
    ("hidden_channels", "ShowHiddenChannels", "list channels you can't read with a 🔒", False),
    ("pin_dms", "PinDMs", "pin DMs to the top of the list (right click a DM)", True),
    ("member_count", "MemberCount", "show online and total members in the title bar", True),
    ("show_connections", "ShowConnections", "show someone's linked accounts (Steam, Spotify…) on their profile", True),
    ("anonymise_files", "AnonymiseFileNames", "upload files with random names", False),
    ("reply_timestamp", "ReplyTimestamp", "show when the message you're replying to was sent", True),
    ("valid_reply", "ValidReply", "fetch replied-to messages that aren't loaded instead of saying deleted", True),
    ("unindent", "Unindent", "trim the extra indent from code blocks", True),
    ("text_replace", "TextReplace", "swap words in messages you send, set the swaps below", True),
    ("send_timestamps", "SendTimestamps", "<t:18:30> or <t:+2h> become timestamps in everyone's own time", True),
    ("keyword_notify", "KeywordNotify", "notify you when a message says one of your words, set them below", True),
    ("fix_embeds", "FixEmbeds", "send x.com, twitter.com and reddit.com links as fxtwitter and rxddit so they embed", False),
    ("owner_crown", "OwnerCrown", "show 👑 next to the server owner", True),
    ("split_long", "SplitLongMessages", "messages over 2000 characters are sent in parts instead of failing", True),
    ("moyai", "Moyai", "🗿", False),
)
DEFAULTS = {key: on for key, _n, _d, on in PLUGINS}


def enabled(cfg, key: str) -> bool:
    return bool((cfg.get("plugins") or {}).get(key, DEFAULTS.get(key, False)))


def toggle(cfg, key: str) -> bool:
    plugins = dict(cfg.get("plugins") or {})
    plugins[key] = not enabled(cfg, key)
    cfg["plugins"] = plugins
    cfg.save()
    return plugins[key]


#clearurls

_TRACKING = re.compile(
    r"^(utm_\w+|fbclid|gclid|dclid|gbraid|wbraid|msclkid|mc_eid|mc_cid|igshid|igsh|yclid|ttclid|twclid"
    r"|_hsenc|_hsmi|mkt_tok|ref_src|ref_url|si|feature|pp|share_id|trk|trkCampaign)$"
)
#si and feature are only junk on these, elsewhere they can mean something
_SHARE_ONLY = {"si": ("youtube.com", "youtu.be", "spotify.com"), "feature": ("youtube.com", "youtu.be"),
               "pp": ("youtube.com",)}
_URL = re.compile(r"https?://[^\s<>|]+")


def _clean(url: str) -> str:
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    if not parts.query:
        return url
    host = parts.netloc.lower()
    keep = []
    for k, v in parse_qsl(parts.query, keep_blank_values=True):
        junk = bool(_TRACKING.match(k))
        if junk and k in _SHARE_ONLY:
            junk = any(host.endswith(h) for h in _SHARE_ONLY[k])
        if host.endswith(("twitter.com", "x.com")) and k in ("s", "t"):
            junk = True
        if not junk:
            keep.append((k, v))
    return urlunsplit(parts._replace(query=urlencode(keep, doseq=True)))


def clearUrls(text: str) -> str:
    return _URL.sub(lambda m: _clean(m.group(0)), text)


#textreplace

def textReplace(text: str, rules: dict) -> str:
    for old, new in (rules or {}).items():
        if old:
            text = re.sub(rf"(?<!\w){re.escape(old)}(?!\w)", lambda _m, n=new: n, text)
    return text


MAX_RULES = 100
MAX_KEYWORDS = 50


def parseRules(text: str) -> dict:
    rules = {}
    for part in (text or "").split(";"):
        old, sep, new = part.partition("=>")
        old, new = old.strip(), new.strip()
        if sep and old and len(old) <= 100 and len(new) <= 500 and len(rules) < MAX_RULES:
            rules[old] = new
    return rules


def formatRules(rules: dict) -> str:
    return "; ".join(f"{k} => {v}" for k, v in (rules or {}).items())


def parseKeywords(text: str) -> list:
    out = []
    for w in (text or "").split(","):
        w = w.strip().lower()
        if w and len(w) <= 64 and w not in out and len(out) < MAX_KEYWORDS:
            out.append(w)
    return out


#splitlongmessages

MESSAGE_LIMIT = 2000
_FENCE = re.compile(r"```(?:([\w+\-]*)\n)?")


#cuts at a line break or a space where it can, and closes and reopens a code block that spans two parts
def splitMessage(text: str, limit: int = MESSAGE_LIMIT) -> list:
    if len(text) <= limit:
        return [text]
    parts = []
    fence = None
    rest = text
    while rest:
        prefix = "" if fence is None else f"```{fence}\n"
        if len(prefix) + len(rest) <= limit:
            parts.append(prefix + rest)
            break
        room = limit - len(prefix) - 4
        cut = rest.rfind("\n", 0, room + 1)
        if cut < room // 2:
            cut = rest.rfind(" ", 0, room + 1)
        if cut < room // 2:
            cut = room
        chunk, rest = rest[:cut], rest[cut:]
        if rest[:1] in ("\n", " "):
            rest = rest[1:]
        for match in _FENCE.finditer(chunk):
            fence = (match.group(1) or "") if fence is None else None
        if fence is not None:
            chunk += "\n```"
        if (prefix + chunk).strip():
            parts.append(prefix + chunk)
    return parts


#sendtimestamps

_STAMP = re.compile(r"<t:(?:(?P<date>\d{4}-\d{2}-\d{2}) )?(?P<h>\d{1,2}):(?P<m>\d{2})>|<t:\+(?P<n>\d{1,4})(?P<unit>[mhd])>")


def sendTimestamps(text: str, now=None) -> str:
    from datetime import datetime, timedelta

    now = now or datetime.now().astimezone()

    def stamp(mt: re.Match) -> str:
        if mt.group("n"):
            secs = int(mt.group("n")) * {"m": 60, "h": 3600, "d": 86400}[mt.group("unit")]
            return f"<t:{int(now.timestamp()) + secs}:R>"
        h, m = int(mt.group("h")), int(mt.group("m"))
        if h > 23 or m > 59:
            return mt.group(0)
        if mt.group("date"):
            try:
                day = datetime.strptime(mt.group("date"), "%Y-%m-%d").replace(tzinfo=now.tzinfo)
            except ValueError:
                return mt.group(0)
            return f"<t:{int(day.replace(hour=h, minute=m).timestamp())}:f>"
        when = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if when < now - timedelta(minutes=1):
            when += timedelta(days=1)
        return f"<t:{int(when.timestamp())}:t>"

    return _STAMP.sub(stamp, text)


#keywordnotify

def keywordHit(text: str, words) -> bool:
    if not text or not words:
        return False
    low = text.lower()
    return any(re.search(rf"(?<!\w){re.escape(w.lower())}(?!\w)", low) for w in words if w)


#fixembeds

_EMBED_HOSTS = {"x.com": "fixupx.com", "twitter.com": "fxtwitter.com", "reddit.com": "rxddit.com"}


def _fixHost(url: str) -> str:
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    host = (parts.hostname or "").lower()
    bare = host[4:] if host.startswith("www.") else host
    bare = bare[4:] if bare.startswith("old.") else bare
    swap = _EMBED_HOSTS.get(bare)
    if swap is None or parts.port is not None:
        return url
    return urlunsplit(parts._replace(netloc=swap))


def fixEmbeds(text: str) -> str:
    return _URL.sub(lambda m: _fixHost(m.group(0)), text)
