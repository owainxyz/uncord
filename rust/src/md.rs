use fancy_regex::Regex as FancyRegex;
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use regex::Regex;
use std::sync::LazyLock;

#[derive(Clone, Default, PartialEq)]
pub struct Look {
    bold: Option<bool>,
    dim: Option<bool>,
    italic: Option<bool>,
    underline: Option<bool>,
    strike: Option<bool>,
    color: Option<String>,
    bgcolor: Option<String>,
    link: Option<String>,
}

impl Look {
    fn plus(&self, other: &Look) -> Look {
        Look {
            bold: other.bold.or(self.bold),
            dim: other.dim.or(self.dim),
            italic: other.italic.or(self.italic),
            underline: other.underline.or(self.underline),
            strike: other.strike.or(self.strike),
            color: other.color.clone().or_else(|| self.color.clone()),
            bgcolor: other.bgcolor.clone().or_else(|| self.bgcolor.clone()),
            link: other.link.clone().or_else(|| self.link.clone()),
        }
    }

    fn isEmpty(&self) -> bool {
        *self == Look::default()
    }

    fn color(c: &str) -> Look {
        Look { color: Some(c.into()), ..Default::default() }
    }

    fn fromTuple(t: &Bound<'_, PyTuple>) -> PyResult<Look> {
        let flag = |i: usize| -> PyResult<Option<bool>> { t.get_item(i)?.extract() };
        let text = |i: usize| -> PyResult<Option<String>> { t.get_item(i)?.extract() };
        Ok(Look {
            bold: flag(0)?,
            dim: flag(1)?,
            italic: flag(2)?,
            underline: flag(3)?,
            strike: flag(4)?,
            color: text(5)?,
            bgcolor: text(6)?,
            link: text(7)?,
        })
    }

    fn toTuple<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyTuple>> {
        PyTuple::new(
            py,
            [
                self.bold.into_pyobject(py)?.into_any(),
                self.dim.into_pyobject(py)?.into_any(),
                self.italic.into_pyobject(py)?.into_any(),
                self.underline.into_pyobject(py)?.into_any(),
                self.strike.into_pyobject(py)?.into_any(),
                self.color.clone().into_pyobject(py)?.into_any(),
                self.bgcolor.clone().into_pyobject(py)?.into_any(),
                self.link.clone().into_pyobject(py)?.into_any(),
            ],
        )
    }
}

fn flag(set: impl Fn(&mut Look)) -> Look {
    let mut l = Look::default();
    set(&mut l);
    l
}

static INLINE: LazyLock<FancyRegex> = LazyLock::new(|| {
    FancyRegex::new(concat!(
        r"(?s)(?P<code>`+)(?P<codebody>.+?)(?P=code)",
        r"|\|\|(?P<spoiler>.+?)\|\|",
        r"|\*\*\*(?P<bi>.+?)\*\*\*",
        r"|\*\*(?P<b>.+?)\*\*",
        r"|__(?P<u>.+?)__",
        r"|\*(?P<i>[^*\s](?:[^*]*?[^*\s])?)\*",
        r"|(?<![\w])_(?P<i2>[^_\s](?:[^_]*?[^_\s])?)_(?![\w])",
        r"|~~(?P<s>.+?)~~",
        r"|\[(?P<ltext>[^\]\n]+)\]\(<?(?P<lurl>https?://[^)\s>]+)>?\)",
        r"|<(?P<aurl>https?://[^>\s]+)>",
        r#"|(?P<url>https?://[^\s<>]+[^\s<>.,:;"')\]!?*_~|])"#,
        r"|<(?P<anim>a?):(?P<ename>\w+):(?P<eid>\d+)>",
        r"|<t:(?P<ts>-?\d+)(?::(?P<tsfmt>[tTdDfFR]))?>",
        r"|<@!?(?P<uid>\d+)>",
        r"|<@&(?P<rid>\d+)>",
        r"|<#(?P<cid>\d+)>",
        r"|</(?P<cmd>[\w\- ]+):\d+>",
        r"|(?P<everyone>@everyone|@here)",
    ))
    .unwrap()
});
static SPECIAL: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[`|*_~\[<@]|https?://").unwrap());
static HEADING: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^(#{1,3}) (.+)").unwrap());
static BULLET: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^(\s*)[-*] (.+)").unwrap());
static NUMBERED: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^(\s*)(\d{1,3})\. (.+)").unwrap());

const LINK_COLOR: &str = "#00a8fc";

struct Out {
    plain: String,
    chars: usize,
    spans: Vec<(usize, usize, Look)>,
}

impl Out {
    fn new() -> Self {
        Out { plain: String::new(), chars: 0, spans: Vec::new() }
    }

    fn push(&mut self, text: &str, look: &Look) {
        if text.is_empty() {
            return;
        }
        let n = text.chars().count();
        if !look.isEmpty() {
            self.spans.push((self.chars, self.chars + n, look.clone()));
        }
        self.plain.push_str(text);
        self.chars += n;
    }

    fn pushPiece(&mut self, piece: Option<(String, Look)>) {
        if let Some((text, look)) = piece {
            self.push(&text, &look);
        }
    }
}

#[allow(non_snake_case)]
fn shortUrl(url: &str) -> String {
    let rest = match url.find(':') {
        Some(i) => &url[i + 1..],
        None => url,
    };
    let (netloc, after) = if let Some(r) = rest.strip_prefix("//") {
        let end = r.find(['/', '?', '#']).unwrap_or(r.len());
        (&r[..end], &r[end..])
    } else {
        ("", rest)
    };
    let after = after.split('#').next().unwrap_or("");
    let (path, query) = match after.find('?') {
        Some(i) => (&after[..i], &after[i + 1..]),
        None => (after, ""),
    };
    let host = netloc.strip_prefix("www.").unwrap_or(netloc);
    let mut path = path.trim_end_matches('/').to_string();
    if (host.contains("discordapp") || host.contains("discord.com")) && path.contains("/attachments/") {
        let last = path.rsplit('/').next().unwrap_or("");
        return if last.is_empty() { host.to_string() } else { last.to_string() };
    }
    if !query.is_empty() && (host.ends_with("youtube.com") || host.ends_with("google.com")) {
        path.push('?');
        path.push_str(query);
    }
    let label = format!("{host}{path}");
    if label.chars().count() <= 42 {
        label
    } else {
        let mut cut: String = label.chars().take(41).collect();
        cut.push('…');
        cut
    }
}

struct Ctx<'py> {
    resolve: Bound<'py, PyAny>,
    reveal: bool,
}

impl<'py> Ctx<'py> {
    fn ask(&self, kind: &str, a: &str, b: Option<&str>) -> PyResult<Option<(String, Look)>> {
        let got = self.resolve.call1((kind, a, b))?;
        if got.is_none() {
            return Ok(None);
        }
        let t = got.cast::<PyTuple>()?;
        let text: String = t.get_item(0)?.extract()?;
        let look = Look::fromTuple(&t.get_item(1)?.cast::<PyTuple>()?.clone())?;
        Ok(Some((text, look)))
    }
}

#[allow(non_snake_case)]
fn inline(text: &str, ctx: &Ctx, base: &Look, out: &mut Out) -> PyResult<()> {
    if !SPECIAL.is_match(text) {
        out.push(text, base);
        return Ok(());
    }
    let mut pos = 0;
    let mut at = 0;
    while at <= text.len() {
        let Some(caps) = INLINE.captures_from_pos(text, at).ok().flatten() else { break };
        let whole = caps.get(0).unwrap();
        if whole.start() > pos {
            out.push(&text[pos..whole.start()], base);
        }
        pos = whole.end();
        at = if whole.end() > whole.start() { whole.end() } else { whole.end() + 1 };
        let g = |name: &str| caps.name(name).map(|m| m.as_str());
        if let Some(body) = g("codebody") {
            let code = g("code").unwrap_or("");
            let shown = if code == "`" { body.trim_matches('`') } else { body };
            out.push(shown, &base.plus(&Look::color("cyan")));
        } else if let Some(sp) = g("spoiler") {
            if ctx.reveal {
                let start = out.chars;
                inline(sp, ctx, base, out)?;
                let end = out.chars;
                if end > start {
                    out.spans.push((start, end, flag(|l| {
                        l.underline = Some(true);
                        l.color = Some("bright_black".into());
                    })));
                }
            } else {
                let mut inner = Out::new();
                inline(sp, ctx, base, &mut inner)?;
                let n = inner.chars.min(40).max(3);
                out.push(&"▒".repeat(n), &Look {
                    color: Some("bright_black".into()),
                    bgcolor: Some("bright_black".into()),
                    ..Default::default()
                });
            }
        } else if let Some(t) = g("bi") {
            inline(t, ctx, &base.plus(&flag(|l| { l.bold = Some(true); l.italic = Some(true); })), out)?;
        } else if let Some(t) = g("b") {
            inline(t, ctx, &base.plus(&flag(|l| l.bold = Some(true))), out)?;
        } else if let Some(t) = g("u") {
            inline(t, ctx, &base.plus(&flag(|l| l.underline = Some(true))), out)?;
        } else if let Some(t) = g("i").or_else(|| g("i2")) {
            inline(t, ctx, &base.plus(&flag(|l| l.italic = Some(true))), out)?;
        } else if let Some(t) = g("s") {
            inline(t, ctx, &base.plus(&flag(|l| l.strike = Some(true))), out)?;
        } else if let Some(label) = g("ltext") {
            let url = g("lurl").unwrap_or("");
            out.push(label, &linkLook(url));
            out.pushPiece(ctx.ask("masked", label, Some(url))?);
        } else if let Some(url) = g("aurl").or_else(|| g("url")) {
            out.push(&shortUrl(url), &linkLook(url));
            if !url.is_ascii() || url.contains("xn--") {
                out.pushPiece(ctx.ask("lookalike", url, None)?);
            }
        } else if let Some(name) = g("ename") {
            let ext = if g("anim").unwrap_or("").is_empty() { "png" } else { "gif" };
            let url = format!("https://cdn.discordapp.com/emojis/{}.{}", g("eid").unwrap_or(""), ext);
            out.push(&format!(":{name}:"), &Look {
                color: Some("yellow".into()),
                link: Some(url),
                ..Default::default()
            });
        } else if let Some(ts) = g("ts") {
            match ctx.ask("ts", ts, g("tsfmt"))? {
                Some((shown, _)) => out.push(&shown, &base.plus(&flag(|l| l.underline = Some(true)))),
                None => out.push(whole.as_str(), base),
            }
        } else if let Some(id) = g("uid") {
            out.pushPiece(ctx.ask("user", id, None)?);
        } else if let Some(id) = g("rid") {
            out.pushPiece(ctx.ask("role", id, None)?);
        } else if let Some(id) = g("cid") {
            out.pushPiece(ctx.ask("channel", id, None)?);
        } else if let Some(cmd) = g("cmd") {
            out.pushPiece(ctx.ask("command", cmd, None)?);
        } else if let Some(who) = g("everyone") {
            out.pushPiece(ctx.ask("everyone", who, None)?);
        }
    }
    if pos < text.len() {
        out.push(&text[pos..], base);
    }
    Ok(())
}

#[allow(non_snake_case)]
fn linkLook(url: &str) -> Look {
    Look {
        color: Some(LINK_COLOR.into()),
        underline: Some(true),
        link: Some(url.into()),
        ..Default::default()
    }
}

fn lines(text: &str, ctx: &Ctx, out: &mut Out) -> PyResult<()> {
    let grey = Look::color("bright_black");
    let none = Look::default();
    let mut quote = false;
    for (i, raw) in text.split('\n').enumerate() {
        if i > 0 {
            out.push("\n", &Look::default());
        }
        let mut line = raw;
        if let Some(r) = line.strip_prefix(">>> ") {
            quote = true;
            line = r;
        }
        if quote || line.starts_with("> ") || line == ">" {
            let body = if quote { line } else { line.get(2..).unwrap_or("") };
            out.push("▎ ", &grey);
            inline(body, ctx, if body.is_empty() { &grey } else { &none }, out)?;
            continue;
        }
        if let Some(c) = HEADING.captures(line) {
            let level = c.get(1).unwrap().as_str().len();
            let look = flag(|l| {
                l.bold = Some(true);
                l.underline = Some(level == 1);
            });
            inline(c.get(2).unwrap().as_str(), ctx, &look, out)?;
            continue;
        }
        if let Some(r) = line.strip_prefix("-# ") {
            inline(r, ctx, &flag(|l| l.dim = Some(true)), out)?;
            continue;
        }
        if let Some(c) = BULLET.captures(line) {
            out.push(&format!("{}• ", &c[1]), &Look::default());
            inline(c.get(2).unwrap().as_str(), ctx, &Look::default(), out)?;
            continue;
        }
        if let Some(c) = NUMBERED.captures(line) {
            out.push(&format!("{}{}. ", &c[1], &c[2]), &grey);
            inline(c.get(3).unwrap().as_str(), ctx, &Look::default(), out)?;
            continue;
        }
        inline(line, ctx, &Look::default(), out)?;
    }
    Ok(())
}

#[allow(non_snake_case)]
fn finish<'py>(py: Python<'py>, out: Out) -> PyResult<(String, Vec<(usize, usize, Bound<'py, PyTuple>)>)> {
    let mut spans = Vec::with_capacity(out.spans.len());
    for (s, e, look) in out.spans {
        spans.push((s, e, look.toTuple(py)?));
    }
    Ok((out.plain, spans))
}

#[pyfunction]
#[pyo3(name = "mdLines")]
#[allow(non_snake_case)]
pub fn mdLines<'py>(
    py: Python<'py>,
    text: &str,
    resolve: Bound<'py, PyAny>,
    reveal: bool,
) -> PyResult<(String, Vec<(usize, usize, Bound<'py, PyTuple>)>)> {
    let ctx = Ctx { resolve, reveal };
    let mut out = Out::new();
    lines(text, &ctx, &mut out)?;
    finish(py, out)
}

#[pyfunction]
#[pyo3(name = "mdInline", signature = (text, resolve, reveal, base=None))]
#[allow(non_snake_case)]
pub fn mdInline<'py>(
    py: Python<'py>,
    text: &str,
    resolve: Bound<'py, PyAny>,
    reveal: bool,
    base: Option<Bound<'py, PyTuple>>,
) -> PyResult<(String, Vec<(usize, usize, Bound<'py, PyTuple>)>)> {
    let ctx = Ctx { resolve, reveal };
    let base = match base {
        Some(t) => Look::fromTuple(&t)?,
        None => Look::default(),
    };
    let mut out = Out::new();
    inline(text, &ctx, &base, &mut out)?;
    finish(py, out)
}

#[pyfunction]
#[pyo3(name = "shortUrl")]
#[allow(non_snake_case)]
pub fn shortUrlPy(url: &str) -> String {
    shortUrl(url)
}
