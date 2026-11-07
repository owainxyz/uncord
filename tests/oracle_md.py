#the python markdown renderer from before the rust port, the rust one has to match it exactly
import textwrap

from rich.style import Style
from rich.text import Text

from uncord.fmt import (MdContext, BLOCKSTART, BULLET, CODE, CODEBLOCK, EMOJI_STYLE, HEADING, INLINE, MENTION, MENTION_ME, NUMBERED,
                        SPECIAL, SPOILER, channelName, formatTs, highlight, link, lookalikeHint, maskedHint,
                        termColour)
from uncord import fmt
from urllib.parse import urlsplit

UNINDENT = True


def mdInline(text: str, ctx: MdContext, base: Style = Style()) -> Text:
    if SPECIAL.search(text) is None:
        plain = Text()
        plain.append(text, style=base)
        return plain
    out = Text()
    pos = 0
    for mt in INLINE.finditer(text):
        if mt.start() > pos:
            out.append(text[pos : mt.start()], style=base)
        pos = mt.end()
        g = mt.groupdict()
        if g["codebody"] is not None:
            out.append(g["codebody"].strip("`") if g["code"] == "`" else g["codebody"], style=base + CODE)
        elif g["spoiler"] is not None:
            inner = mdInline(g["spoiler"], ctx, base)
            if ctx.reveal:
                inner.stylize(Style(underline=True, color="bright_black"))
                out.append_text(inner)
            else:
                out.append("▒" * max(3, min(len(inner.plain), 40)), style=SPOILER)
        elif g["bi"] is not None:
            out.append_text(mdInline(g["bi"], ctx, base + Style(bold=True, italic=True)))
        elif g["b"] is not None:
            out.append_text(mdInline(g["b"], ctx, base + Style(bold=True)))
        elif g["u"] is not None:
            out.append_text(mdInline(g["u"], ctx, base + Style(underline=True)))
        elif g["i"] is not None or g["i2"] is not None:
            out.append_text(mdInline(g["i"] or g["i2"], ctx, base + Style(italic=True)))
        elif g["s"] is not None:
            out.append_text(mdInline(g["s"], ctx, base + Style(strike=True)))
        elif g["ltext"] is not None:
            out.append_text(link(g["ltext"], g["lurl"]))
            out.append_text(maskedHint(g["ltext"], g["lurl"]))
        elif g["aurl"] is not None or g["url"] is not None:
            url = g["aurl"] or g["url"]
            out.append_text(link(shortUrl(url), url))
            if not url.isascii() or "xn--" in url:
                out.append_text(lookalikeHint(url))
        elif g["ename"] is not None:
            url = f"https://cdn.discordapp.com/emojis/{g['eid']}.{'gif' if g['anim'] else 'png'}"
            out.append_text(link(f":{g['ename']}:", url, EMOJI_STYLE))
        elif g["ts"] is not None:
            try:
                out.append(formatTs(int(g["ts"]), g["tsfmt"]), style=base + Style(underline=True))
            except (ValueError, OverflowError, OSError):
                out.append(mt.group(), style=base)
        elif g["uid"] is not None:
            uid = int(g["uid"])
            u = ctx.users.get(uid)
            name = u.display_name if u is not None else "unknown-user"
            out.append(f"@{name}", style=MENTION_ME if uid == ctx.meId else MENTION)
        elif g["rid"] is not None:
            r = ctx.roles.get(int(g["rid"]))
            colour = termColour(getattr(r, "colour", None)) if r is not None else None
            out.append(
                f"@{r.name if r is not None else 'deleted-role'}",
                style=Style(color=colour or "cyan", bold=True),
            )
        elif g["cid"] is not None:
            ch = ctx.get_channel(int(g["cid"]))
            out.append(f"#{channelName(ch) if ch is not None else 'unknown'}", style=MENTION)
        elif g["cmd"] is not None:
            out.append(f"/{g['cmd']}", style=MENTION)
        elif g["everyone"] is not None:
            out.append(g["everyone"], style=MENTION_ME)
    if pos < len(text):
        out.append(text[pos:], style=base)
    return out


def mdLines(text: str, ctx: MdContext) -> Text:
    out = Text()
    lines = text.split("\n")
    inBlockQuote = False
    for i, line in enumerate(lines):
        if i:
            out.append("\n")
        if line.startswith(">>> "):
            inBlockQuote = True
            line = line[4:]
        if inBlockQuote or line.startswith("> ") or line == ">":
            body = line if inBlockQuote else line[2:]
            out.append("▎ ", style="bright_black")
            out.append_text(mdInline(body, ctx, Style(color="bright_black") if not body else Style()))
            continue
        m = HEADING.match(line)
        if m:
            out.append_text(mdInline(m.group(2), ctx, Style(bold=True, underline=len(m.group(1)) == 1)))
            continue
        if line.startswith("-# "):
            out.append_text(mdInline(line[3:], ctx, Style(dim=True)))
            continue
        m = BULLET.match(line)
        if m:
            out.append(m.group(1) + "• ")
            out.append_text(mdInline(m.group(2), ctx))
            continue
        m = NUMBERED.match(line)
        if m:
            out.append(f"{m.group(1)}{m.group(2)}. ", style="bright_black")
            out.append_text(mdInline(m.group(3), ctx))
            continue
        out.append_text(mdInline(line, ctx))
    return out


def markdown(text: str, ctx: MdContext) -> Text:
    if "```" not in text:
        fast = mdInline(text, ctx) if "\n" not in text and BLOCKSTART.match(text) is None else mdLines(text, ctx)
        fast.rstrip()
        return fast
    out = Text()
    pos = 0
    for mt in CODEBLOCK.finditer(text):
        before = text[pos : mt.start()]
        if before.strip("\n"):
            out.append_text(mdLines(before.strip("\n"), ctx))
            out.append("\n")
        code = mt.group(2).strip("\n")
        if fmt.UNINDENT:
            code = textwrap.dedent(code)
        lang = (mt.group(1) or "").lower()
        if lang:
            out.append(f"┏ {lang}\n", style="bright_black")
        for j, cl in enumerate(highlight(code, lang).split("\n")):
            if j:
                out.append("\n")
            out.append("┃ ", style="bright_black")
            out.append_text(cl)
        out.append("\n")
        pos = mt.end()
    rest = text[pos:]
    if rest.strip("\n") or not out:
        out.append_text(mdLines(rest.strip("\n") if out else rest, ctx))
    out.rstrip()
    return out


def shortUrl(url: str) -> str:
    u = urlsplit(url)
    host = u.netloc.removeprefix("www.")
    path = u.path.rstrip("/")
    if ("discordapp" in host or "discord.com" in host) and "/attachments/" in path:
        return path.rsplit("/", 1)[-1] or host
    if u.query and host.endswith(("youtube.com", "google.com")):
        path += "?" + u.query
    label = host + path
    return label if len(label) <= 42 else label[:41] + "…"
